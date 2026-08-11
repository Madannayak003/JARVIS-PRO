import threading
import queue
from pathlib import Path

from voice.manager import (
    speak,
    prepare_speech,
    play_prepared_speech,
)

from voice.state import (
    is_current,
    is_cancelled,
)


# =========================================================
# PRO TTS PIPELINE
#
# Stage 1:
#     Sentence Queue
#
# Stage 2:
#     TTS Prefetch Worker
#
# Stage 3:
#     Audio Queue
#
# Stage 4:
#     Playback Worker
#
# This allows:
#
# Sentence 1 → play
# Sentence 2 → generate while #1 plays
# Sentence 3 → generate while #2 plays
#
# =========================================================


class TTSPipeline:

    def __init__(
        self,
        stop_event,
        session,
    ):

        self.stop_event = stop_event

        self.session = session

        # -------------------------------------------------
        # Incoming sentences
        # -------------------------------------------------

        self.sentence_queue = queue.Queue(
            maxsize=4
        )

        # -------------------------------------------------
        # Prepared audio files
        #
        # Small buffer prevents excessive generation.
        # -------------------------------------------------

        self.audio_queue = queue.Queue(
            maxsize=2
        )

        # -------------------------------------------------
        # Worker threads
        # -------------------------------------------------

        self.prefetch_thread = None

        self.playback_thread = None

        # -------------------------------------------------
        # Running state
        # -------------------------------------------------

        self.started = False

        self.finished = False

    # =====================================================
    # Cancellation
    # =====================================================

    def cancelled(self):

        return (
            self.stop_event.is_set()
            or self.session.cancel_event.is_set()
            or not is_current(self.session)
            or is_cancelled(self.session)
        )

    # =====================================================
    # Start
    # =====================================================

    def start(self):

        if self.started:

            return

        self.started = True

        self.prefetch_thread = threading.Thread(

            target=self._prefetch_worker,

            daemon=True,

            name="JARVIS-TTS-Prefetch",

        )

        self.playback_thread = threading.Thread(

            target=self._playback_worker,

            daemon=True,

            name="JARVIS-TTS-Playback",

        )

        self.prefetch_thread.start()

        self.playback_thread.start()

        print(
            "[TTS PIPELINE] Started"
        )

    # =====================================================
    # Add Sentence
    # =====================================================

    def put(self, sentence):

        if not sentence:

            return False

        if self.cancelled():

            return False

        # -------------------------------------------------
        # Wait until there is room.
        #
        # This naturally creates back-pressure.
        # -------------------------------------------------

        while not self.cancelled():

            try:

                self.sentence_queue.put(
                    sentence,
                    timeout=0.05
                )

                return True

            except queue.Full:

                continue

        return False

    # =====================================================
    # Finish Input
    # =====================================================

    def finish(self):

        if self.finished:

            return

        self.finished = True

        # -------------------------------------------------
        # Tell prefetch worker that no more sentences
        # will arrive.
        # -------------------------------------------------

        while not self.cancelled():

            try:

                self.sentence_queue.put(
                    None,
                    timeout=0.05
                )

                return

            except queue.Full:

                continue

    # =====================================================
    # Prefetch Worker
    #
    # Generates audio ahead of playback.
    # =====================================================

    def _prefetch_worker(self):

        while True:

            if self.cancelled():

                self._cleanup_audio_queue()

                return

            try:

                sentence = self.sentence_queue.get(
                    timeout=0.05
                )

            except queue.Empty:

                continue

            # -------------------------------------------------
            # End of sentence stream
            # -------------------------------------------------

            if sentence is None:

                self.sentence_queue.task_done()

                # -------------------------------------------------
                # Tell playback worker that generation is finished.
                # -------------------------------------------------

                while not self.cancelled():

                    try:

                        self.audio_queue.put(
                            None,
                            timeout=0.05
                        )

                        return

                    except queue.Full:

                        continue

                return

            try:

                if self.cancelled():

                    return

                # -------------------------------------------------
                # Clean sentence
                # -------------------------------------------------

                sentence = sentence.strip()

                if not sentence:

                    continue

                # -------------------------------------------------
                # Generate audio BEFORE playback.
                #
                # This is the key PRO optimization.
                # -------------------------------------------------

                audio_file = prepare_speech(
                    sentence,
                    self.session,
                )

                # -------------------------------------------------
                # If Edge TTS isn't available, use fallback.
                #
                # None means no prepared audio.
                # -------------------------------------------------

                if audio_file is None:

                    if not self.cancelled():

                        self._play_fallback(
                            sentence
                        )

                    continue

                # -------------------------------------------------
                # Session could have changed while generating.
                # -------------------------------------------------

                if self.cancelled():

                    self._delete_audio(
                        audio_file
                    )

                    return

                # -------------------------------------------------
                # Put prepared audio into playback queue.
                # -------------------------------------------------

                while not self.cancelled():

                    try:

                        self.audio_queue.put(
                            (
                                audio_file,
                                sentence,
                            ),
                            timeout=0.05
                        )

                        audio_file = None

                        break

                    except queue.Full:

                        continue

                # -------------------------------------------------
                # If cancellation happened before the file was
                # handed to playback, clean it up.
                # -------------------------------------------------

                if audio_file is not None:

                    self._delete_audio(
                        audio_file
                    )

                    return

            except Exception as e:

                print(
                    "[TTS PREFETCH ERROR]",
                    e
                )

            finally:

                self.sentence_queue.task_done()

    # =====================================================
    # Playback Worker
    # =====================================================

    def _playback_worker(self):

        while True:

            if self.cancelled():

                self._cleanup_audio_queue()

                return

            try:

                item = self.audio_queue.get(
                    timeout=0.05
                )

            except queue.Empty:

                continue

            # -------------------------------------------------
            # Generation finished
            # -------------------------------------------------

            if item is None:

                self.audio_queue.task_done()

                return

            audio_file, sentence = item

            try:

                if self.cancelled():

                    self._delete_audio(
                        audio_file
                    )

                    return

                # -------------------------------------------------
                # PLAY PREPARED AUDIO
                #
                # While this is playing, the prefetch worker is
                # already generating the next sentence.
                # -------------------------------------------------

                play_prepared_speech(
                    audio_file,
                    self.session,
                )

            except Exception as e:

                print(
                    "[TTS PLAYBACK ERROR]",
                    e
                )

                self._delete_audio(
                    audio_file
                )

            finally:

                self.audio_queue.task_done()

    # =====================================================
    # Offline / fallback
    # =====================================================

    def _play_fallback(self, sentence):

        if self.cancelled():

            return

        try:

            speak(
                sentence,
                wait=True,
                session=self.session,
            )

        except Exception as e:

            print(
                "[TTS FALLBACK ERROR]",
                e
            )

    # =====================================================
    # Wait
    # =====================================================

    def wait(self):

        if self.prefetch_thread:

            self.prefetch_thread.join()

        if self.playback_thread:

            self.playback_thread.join()

        self._cleanup_audio_queue()

        print(
            "[TTS PIPELINE] Finished"
        )

    # =====================================================
    # Delete Audio
    # =====================================================

    def _delete_audio(self, audio_file):

        if not audio_file:

            return

        try:

            path = Path(
                audio_file
            )

            if path.exists():

                path.unlink()

                print(
                    "[TTS PIPELINE] "
                    f"Deleted: {path.name}"
                )

        except FileNotFoundError:

            pass

        except Exception as e:

            print(
                "[TTS PIPELINE] "
                f"Could not delete audio: {e}"
            )

    # =====================================================
    # Cleanup queued audio
    # =====================================================

    def _cleanup_audio_queue(self):

        while True:

            try:

                item = self.audio_queue.get_nowait()

            except queue.Empty:

                break

            if item is not None:

                audio_file = item[0]

                self._delete_audio(
                    audio_file
                )

            self.audio_queue.task_done()
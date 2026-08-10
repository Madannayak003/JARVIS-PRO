from skills.camera.vision_analyzer import vision_analyzer
from skills.camera.spatial_analyzer import spatial_analyzer


class SceneAnalyzer:

    def analyze(self, detections, frame_width=1280):

        filtered = vision_analyzer.filter_detections(
            detections
        )

        spatial = spatial_analyzer.analyze(
            filtered,
            frame_width
        )

        counts = vision_analyzer.count_objects(
            filtered
        )

        description = self._build_description(
            spatial,
            counts
        )

        return {
            "objects": spatial,
            "counts": counts,
            "description": description
        }

    def _build_description(self, objects, counts):

        if not objects:
            return "I don't see any recognizable objects."

        descriptions = []

        for obj in objects:

            label = obj["label"]
            position = obj["position"]

            count = counts.get(label, 1)

            if count == 1:
                object_name = f"one {label}"
            else:
                object_name = f"{count} {label}s"

            descriptions.append(
                f"{object_name} in the {position}"
            )

        if len(descriptions) == 1:
            return f"I can see {descriptions[0]}."

        if len(descriptions) == 2:
            return (
                f"I can see {descriptions[0]} "
                f"and {descriptions[1]}."
            )

        return (
            "I can see "
            + ", ".join(descriptions[:-1])
            + f", and {descriptions[-1]}."
        )


scene_analyzer = SceneAnalyzer()
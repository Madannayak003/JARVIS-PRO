class SpatialAnalyzer:

    def __init__(self, frame_width=1280):
        self.frame_width = frame_width

    def get_position(self, box, frame_width=None):
        """
        Determine whether an object is on the left,
        center, or right side of the frame.
        """

        width = frame_width or self.frame_width

        x1, y1, x2, y2 = box

        center_x = (x1 + x2) / 2

        left_boundary = width / 3
        right_boundary = (width * 2) / 3

        if center_x < left_boundary:
            return "left"

        if center_x > right_boundary:
            return "right"

        return "center"

    def analyze(self, detections, frame_width=None):

        width = frame_width or self.frame_width

        results = []

        for detection in detections:

            box = detection.get("box")

            if not box:
                continue

            position = self.get_position(
                box,
                width
            )

            results.append({
                **detection,
                "position": position
            })

        return results


spatial_analyzer = SpatialAnalyzer()
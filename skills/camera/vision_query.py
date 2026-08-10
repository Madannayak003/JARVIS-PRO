from skills.camera.vision_loop import vision_loop


class VisionQuery:

    def get_scene(self):

        return vision_loop.get_scene()

    def describe(self):

        scene = self.get_scene()

        if not scene:
            return "I don't have a current vision scene."

        return scene.get(
            "description",
            "I don't see anything recognizable."
        )

    def count(self, object_name):

        scene = self.get_scene()

        if not scene:
            return 0

        counts = scene.get("counts", {})

        return counts.get(
            object_name.lower().strip(),
            0
        )

    def has_object(self, object_name):

        return self.count(object_name) > 0

    def objects(self):

        scene = self.get_scene()

        if not scene:
            return []

        return scene.get("objects", [])

    def objects_at(self, position):

        position = position.lower().strip()

        objects = [
            obj
            for obj in self.objects()
            if obj.get("position") == position
        ]

        if not objects:
            return f"I don't see anything on your {position}."

        labels = [
            obj.get("label", "something")
            for obj in objects
        ]

        if len(labels) == 1:
            return f"I can see one {labels[0]} on your {position}."

        if len(labels) == 2:
            return (
                f"I can see {labels[0]} and {labels[1]} "
                f"on your {position}."
            )

        return (
            f"I can see {len(labels)} objects "
            f"on your {position}."
        )


vision_query = VisionQuery()
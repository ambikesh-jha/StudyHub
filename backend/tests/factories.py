from __future__ import annotations

import factory


class AuthPayloadFactory(factory.Factory):
    class Meta:
        model = dict

    email = factory.Sequence(lambda index: f"user{index}@studyhub.dev")
    password = "Password123!"
    display_name = factory.Sequence(lambda index: f"User {index}")


class ProfilePayloadFactory(factory.Factory):
    class Meta:
        model = dict

    display_name = factory.Sequence(lambda index: f"Member {index}")
    email = factory.Sequence(lambda index: f"member{index}@studyhub.dev")
    bio = "Learning every day"


class CoursePayloadFactory(factory.Factory):
    class Meta:
        model = dict

    title = factory.Sequence(lambda index: f"Course {index}")
    description = "A sample course"
    icon = "book"
    color = "purple"
    is_published = True


from panda3d.core import Vec3
from panda3d.core import CollisionSphere

import wecs

from wecs.aspects import Aspect
from wecs.aspects import factory

from wecs.panda3d.constants import FALLING_MASK
from wecs.panda3d.constants import BUMPING_MASK
from wecs.panda3d.constants import CAMERA_MASK

import behaviors

from avatar_ui import Embodiable


# Map

game_map = Aspect(
    [
        wecs.panda3d.prototype.Model,
        wecs.panda3d.prototype.Geometry,
        wecs.panda3d.prototype.CollidableGeometry,
        # wecs.panda3d.prototype.FlattenStrong,
        # wecs.panda3d.mouseover.MouseOverableGeometry,
        # wecs.panda3d.mouseover.Pointable,
        wecs.panda3d.spawnpoints.SpawnMap,
     ],
    overrides={
        wecs.panda3d.prototype.CollidableGeometry: dict(
            mask=FALLING_MASK|BUMPING_MASK|CAMERA_MASK,
        ),
    },
)


# Props

prop = Aspect(
    [
        wecs.panda3d.prototype.Model,
        wecs.panda3d.prototype.Geometry,
        wecs.panda3d.character.BumpingMovement,
        wecs.panda3d.spawnpoints.SpawnAt,
    ],
)


# There are characters, which are points in space that can be moved
# around using the `CharacterController`, using either player input or
# AI control.

character = Aspect(
    [
        wecs.mechanics.clock.Clock,
        wecs.panda3d.prototype.Model,
        wecs.panda3d.character.CharacterController,
        wecs.panda3d.spawnpoints.SpawnAt,
    ],
    overrides={
        wecs.mechanics.clock.Clock: dict(
            clock=lambda: factory(wecs.mechanics.clock.panda3d_clock),
        ),
        wecs.panda3d.character.CharacterController: dict(
            gravity=Vec3(0, 0, -30),
        ),
    },
)


# Avatars are characters which have (presumably humanoid) animated
# models that can walk around. Their entities can be found using the
# mouse cursor or other collision sensors.

animated = Aspect(
    [
        wecs.panda3d.prototype.Actor,
        wecs.panda3d.animation.Animation,
    ],
)


walking = Aspect(
    [
        wecs.panda3d.character.WalkingMovement,
        wecs.panda3d.character.InertialMovement,
        wecs.panda3d.character.BumpingMovement,
        wecs.panda3d.character.FallingMovement,
        wecs.panda3d.character.JumpingMovement,
    ],
    overrides={
        wecs.panda3d.character.WalkingMovement:dict(
            speed=500.0,
        ),
        wecs.panda3d.character.JumpingMovement:dict(
            impulse=Vec3(0, 0, 10),
        ),
    }
)


avatar = Aspect(
    [
        character,
        animated,
        walking,
        #wecs.panda3d.mouseover.MouseOverable,
        #wecs.panda3d.mouseover.Targetable,
        Embodiable,
    ],
    overrides={
        wecs.panda3d.character.WalkingMovement: dict(
            turning_speed=40.0,
            #turning_speed=540.0,
        ),
    },
)


# Disembodied entities are simply characters that can float.
# FIXME: They should probably also fall/bump into things.

disembodied = Aspect(
    [
        character,
        wecs.panda3d.character.FloatingMovement,
    ],
)


first_person = Aspect(
    [
        wecs.panda3d.camera.Camera,
        wecs.panda3d.camera.MountedCameraMode,
    ],
)


third_person_base = Aspect(
    [
        wecs.panda3d.camera.Camera,
        wecs.panda3d.camera.ObjectCentricCameraMode,
        wecs.panda3d.camera.CollisionZoom,
        wecs.panda3d.character.AutomaticTurningMovement,
    ],
    overrides={
        wecs.panda3d.camera.ObjectCentricCameraMode: dict(
            turning_speed=180.0,
        ),
    },
)


third_person_action = Aspect(
    [
        third_person_base,
        wecs.panda3d.character.TurningBackToCameraMovement,
    ],
    overrides={
        wecs.panda3d.character.TurningBackToCameraMovement: dict(
            view_axis_alignment=0.4,
            threshold=0.2,
        ),
    },
)


third_person_twin_stick = Aspect(
    [
        third_person_base,
        wecs.panda3d.character.CameraReorientedInput,
        wecs.panda3d.character.TwinStickMovement,
    ],
    overrides={
        wecs.panda3d.camera.ObjectCentricCameraMode: dict(
            pitch=-30.0,
        ),
    },
)


# The action camera uses the 'camera_movement' context to rotate the
# camera. Twin stick uses the 'character_direction' context to indicate
# where to face.
third_person = third_person_action
#third_person = third_person_twin_stick


# Player interface / AI.
# Note that these aren't mutually exclusive. Both can exert control over
# the `CharacterController`. If `Input.contexts` includes
# 'character_movement', AI input is overwritten by player input; If it
# doesn't, it isn't.
# The player interface also can control the NPC AI, using the entity to
# send commands to it if no other entity is selected as recipient.

pc_mind = Aspect(
    [
        wecs.panda3d.input.Input,
        #wecs.panda3d.mouseover.MouseOveringCamera,
        #wecs.panda3d.mouseover.UserInterface,
    ],
    overrides={
        wecs.panda3d.input.Input: dict(
            contexts={
                'character_movement',
                #'character_direction',
                'camera_movement',
                'camera_zoom',
                'mouse_over',
                'select_entity',
            },
        ),
    },
)


npc_behaviors = lambda: dict(
    #idle=wecs.panda3d.ai.idle,
    idle=behaviors.idle(),
    walk_to_entity=behaviors.walk_to_entity(),
)


npc_mind = Aspect(
    [
        wecs.panda3d.ai.BehaviorAI,
        #wecs.panda3d.mouseover.Selectable,
    ],
    overrides={
        wecs.panda3d.ai.BehaviorAI: dict(
            behavior=['idle'],
            behaviors=lambda: npc_behaviors(),
        ),
    },
)


# Game Objects, finally!
# An observer is a disembodied, player-controlled character.
# A player_character is a player-controlled avatar
# A non_player_character is an AI-controlled avatar.

observer = Aspect(
    [
        disembodied,
        first_person,
        pc_mind,
    ],
)


player_character = Aspect(
    [
        avatar,
        third_person,
        pc_mind,
        npc_mind,
    ],
)


non_player_character = Aspect(
    [
        avatar,
        npc_mind,
    ],
)


# WECS' default 3D character is Rebecca, and these are her parameters.

def rebecca_bumper():
    return {
        'bumper': dict(
            node_name='bumper',
            #shape=CollisionSphere,
            #center=Vec3(0.0, 0.0, 1.0),
            #radius=0.7,
            debug=True,
        ),
    }


def rebecca_lifter():
    return {
        'lifter': dict(
            node_name='lifter',
            #shape=CollisionSphere,
            #center=Vec3(0.0, 0.0, 0.5),
            #radius=0.5,
            debug=True,
        ),
    }


rebecca = {
    wecs.panda3d.prototype.Geometry: dict(
        file='models/character/rebecca.bam',
    ),
    wecs.panda3d.prototype.Actor: dict(
        file='models/character/rebecca.bam',
    ),
    wecs.panda3d.character.BumpingMovement: dict(
        node_name='bumper',
        tag_name='bumper',
        solids=factory(rebecca_bumper),
        #debug=True,
    ),
    wecs.panda3d.character.FallingMovement: dict(
        node_name='lifter',
        tag_name='lifter',
        solids=factory(rebecca_lifter),
        #debug=True,
    ),
    wecs.panda3d.mouseover.MouseOverable: dict(
        solid=CollisionSphere(0, 0, 1, 1),
    ),
}


# A park bench

bench = {
    wecs.panda3d.prototype.Geometry: dict(
        file='models/props/parkbench.bam',
    ),
    wecs.panda3d.character.BumpingMovement: dict(
        node_name='bumper',
        tag_name='bumper',
        #debug=True,
    ),
}

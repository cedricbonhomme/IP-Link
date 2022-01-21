#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ruth chabay, carnegie mellon university (rchabay@andrew.cmu.edu)
# v1.0 2000-12-17

# Markus Gritsch (gritsch@iue.tuwien.ac.at)
# v.1.1   2001-03-09
#   *) replaced 'scene' by 'display' everywhere
#   *) added spheres at the joints of a curve
#   *) consistent pov_texture usage in process_arrow() also for the shaft
#   *) ambient light, light sources, up, and fov are now handled correctly
#   *) some cosmetic changes to the code
# v.1.1.1 2001-03-22
#   *) added 'shadowless' keyword to export()

# Ruth Chabay
# 2001-06-23
# hack to fix error in export_curve introduced by Python 2.1
# now can't assign obj.color = array(...)

# Markus Gritsch (gritsch@iue.tuwien.ac.at)
# v.1.2   2001-11-23
#   *) added 'xy_ratio' and 'custom_text' keywords to export()
#   *) the pov-strings are now directly written to a file

# Bruce Sherwood
# 2004-07-18
# add dictionary ("legal") for identifying an object so that
# povexport will continue to work with the new Boost-based VPython
# which changes the details returned by object.__class__

## NOTE: when changing this module please change the following string:
from string import rfind
from visual import *

POVEXPORT_VERSION = "povexport 2004-07-18"

"""This module exports a VPython scene as POV-Ray scene description code.
Lights and camera location from the current visual scene are included.
Optionally, you may specify a list of include files, and pov textures for
objects.
For an example of its use, see 'povexample.py'
convex objects are not exported.
"""


legal = {
    frame: "frame",
    sphere: "sphere",
    box: "box",
    cylinder: "cylinder",
    curve: "curve",
    ring: "ring",
    arrow: "arrow",
    cone: "cone",
}
ihat = vector(1, 0, 0)
jhat = vector(0, 1, 0)
khat = vector(0, 0, 1)


def version():
    return POVEXPORT_VERSION


def getpolar(a):
    # a is a vector
    # find rotation angles (standard polar coord)
    xy = sqrt(a.x ** 2 + a.y ** 2)
    theta = atan2(xy, a.z)
    phi = atan2(a.y, a.x)
    return [theta, phi]


def process_frame(a, code):
    # add in frame rotations & translations (may be nested)
    frame_code = ""
    fr = a.frame
    while fr:
        # orientation of frame.axis
        ang = getpolar(fr.axis)
        theta = ang[0]
        phi = ang[1]
        aup = fr.up * 1.0
        # find rotation around x-axis (if fr.up <> jhat)
        # "undo" theta & phi rotations so can find alpha
        aup = rotate(aup, axis=khat, angle=-phi)
        aup = rotate(aup, axis=jhat, angle=pi / 2.0 - theta)
        a_sin = dot(cross(jhat, norm(aup)), ihat)
        a_cos = dot(norm(aup), jhat)
        alpha = atan2(a_sin, a_cos)
        frx = alpha * 180.0 / pi
        fry = -90 + theta * 180.0 / pi
        frz = phi * 180.0 / pi
        rrot = "    rotate <%f, %f, %f>\n"
        ttrn = "    translate <%f, %f, %f>\n"
        frame_code += rrot % (frx, fry, frz)
        frame_code += ttrn % (fr.x, fr.y, fr.z)
        fr = fr.frame

    # insert frame_code at end (these rot's must be done last)
    end = rfind(code, "}")
    code = code[:end] + frame_code + code[end:]
    return code


def add_texture(a, code):
    # add in user-specified texture (will override color)
    if hasattr(a, "pov_texture"):
        tstring = "    texture { " + a.pov_texture + " }\n"
        end = rfind(code, "}")
        code = code[:end] + tstring + code[end:]
    return code


def export_sphere(a):
    sphere_template = """
sphere {
    <%(posx)f, %(posy)f, %(posz)f>, %(radius)f
    pigment { color rgb <%(red)f, %(green)f, %(blue)f> }
}
"""
    object_code = sphere_template % {
        "posx": a.x,
        "posy": a.y,
        "posz": a.z,
        "radius": a.radius,
        "red": a.red,
        "green": a.green,
        "blue": a.blue,
    }
    object_code = process_frame(a, object_code)
    object_code = add_texture(a, object_code)
    return object_code


def export_box(a):
    # create box at origin along x-axis
    # then rotate around x,y,z axes
    # then translate to final location
    box_template = """
box {
    <%(posx)f, %(posy)f, %(posz)f>, <%(pos2x)f, %(pos2y)f, %(pos2z)f>
    pigment {color rgb <%(red)f, %(green)f, %(blue)f>}
    rotate <%(rotx)f, %(roty)f, %(rotz)f>
    translate <%(transx)f, %(transy)f, %(transz)f>
}
"""
    # find rotations
    ang = getpolar(a.axis)
    theta = ang[0]
    phi = ang[1]
    # find rotation around x-axis (if a.up <> jhat)
    # "undo" theta & phi rotations so can find alpha
    aup = a.up * 1.0
    aup = rotate(aup, axis=khat, angle=-phi)
    aup = rotate(aup, axis=jhat, angle=pi / 2.0 - theta)
    a_sin = dot(cross(jhat, norm(aup)), ihat)
    a_cos = dot(norm(aup), jhat)
    alpha = atan2(a_sin, a_cos)
    # pos of visual box is at center
    # generate two opposite corners for povray
    pos1 = vector(0, 0, 0) - a.size / 2.0
    pos2 = vector(0, 0, 0) + a.size / 2.0

    object_code = box_template % {
        "posx": pos1.x,
        "posy": pos1.y,
        "posz": pos1.z,
        "pos2x": pos2.x,
        "pos2y": pos2.y,
        "pos2z": pos2.z,
        "rotx": alpha * 180.0 / pi,
        "roty": -90.0 + theta * 180.0 / pi,
        "rotz": phi * 180.0 / pi,
        "transx": a.x,
        "transy": a.y,
        "transz": a.z,
        "red": a.red,
        "green": a.green,
        "blue": a.blue,
    }
    object_code = process_frame(a, object_code)
    object_code = add_texture(a, object_code)
    return object_code


def export_cylinder(a):
    cylinder_template = """
cylinder {
    <%(posx)f, %(posy)f, %(posz)f>,<%(pos2x)f, %(pos2y)f, %(pos2z)f>, %(radius)f
    pigment { color rgb <%(red)f, %(green)f, %(blue)f> }
}
"""
    endpt1 = a.pos
    endpt2 = a.pos + a.axis
    object_code = cylinder_template % {
        "posx": a.x,
        "posy": a.y,
        "posz": a.z,
        "pos2x": endpt2.x,
        "pos2y": endpt2.y,
        "pos2z": endpt2.z,
        "red": a.red,
        "green": a.green,
        "blue": a.blue,
        "radius": a.radius,
    }
    object_code = process_frame(a, object_code)
    object_code = add_texture(a, object_code)
    return object_code


def export_curve(a):
    object_code = ""
    if len(a.pos) > 1:
        ii = 0
        while ii < len(a.pos) - 1:
            endpt1 = a.pos[ii]
            endpt2 = a.pos[ii + 1]
            if a.radius > 0:
                rr = a.radius
            else:
                rr = mag(endpt1 - endpt2) / 200.0
            # create a dummy cylinder to export
            ccyl = cylinder(
                pos=endpt1,
                axis=endpt2 - endpt1,
                radius=rr,
                color=tuple(a.color[ii]),
                frame=a.frame,
                visible=0,
            )
            csph = sphere(
                pos=endpt1,
                radius=rr,
                color=tuple(a.color[ii]),
                frame=a.frame,
                visible=0,
            )
            if hasattr(a, "pov_texture"):
                ccyl.pov_texture = a.pov_texture
                csph.pov_texture = a.pov_texture
            object_code += export_cylinder(ccyl) + export_sphere(csph)
            ii = ii + 1
        endpt1 = a.pos[ii]
        csph = sphere(
            pos=endpt1, radius=rr, color=tuple(a.color[ii]), frame=a.frame, visible=0
        )
        if hasattr(a, "pov_texture"):
            csph.pov_texture = a.pov_texture
        object_code += export_sphere(csph)
    del ccyl
    del csph
    return object_code


def export_ring(a):
    torus_template = """
torus {
    %(radius)f, %(minorradius)f
    pigment { color rgb <%(red)f, %(green)f, %(blue)f> }
    rotate <0.0, 0.0, -90.0> // align with x-axis
    rotate <%(rotx)f, %(roty)f, %(rotz)f>
    translate <%(transx)f, %(transy)f, %(transz)f>
}
"""
    ang = getpolar(a.axis)
    theta = ang[0]
    phi = ang[1]
    object_code = torus_template % {
        "radius": a.radius,
        "minorradius": a.thickness,
        "transx": a.x,
        "transy": a.y,
        "transz": a.z,
        "rotx": 0.0,
        "roty": -90.0 + theta * 180.0 / pi,
        "rotz": phi * 180.0 / pi,
        "red": a.red,
        "green": a.green,
        "blue": a.blue,
    }
    object_code = process_frame(a, object_code)
    object_code = add_texture(a, object_code)
    return object_code


def export_arrow(a):
    pyramid_template = """
object {Pyramid
    pigment { color rgb <%(red)f, %(green)f, %(blue)f> }
    scale <%(scalex)f, %(scaley)f, %(scalez)f>
    rotate <0, 0, -90> // align with x-axis
    rotate <%(rotx)f, %(roty)f, %(rotz)f>
    translate <%(transx)f, %(transy)f, %(transz)f>
}
"""
    al = a.length
    hl = a.headlength
    sl = al - hl  # length of shaft
    hw = a.headwidth
    sw = a.shaftwidth
    # head is a pyramid
    ppos = a.pos + a.axis * (sl / al)
    ang = getpolar(a.axis)
    theta = ang[0]
    phi = ang[1]
    m1 = pyramid_template % {
        "scalex": hw,
        "scaley": hl,
        "scalez": hw,
        "rotx": 0.0,
        "roty": -90.0 + theta * 180.0 / pi,
        "rotz": phi * 180.0 / pi,
        "red": a.red,
        "green": a.green,
        "blue": a.blue,
        "transx": ppos.x,
        "transy": ppos.y,
        "transz": ppos.z,
    }
    m1 = process_frame(a, m1)
    m1 = add_texture(a, m1)

    # shaft is a box; need to create a dummy box
    abox = box(
        pos=a.pos + a.axis * (sl / al) / 2.0,
        axis=a.axis * (sl / al),
        up=a.up,
        width=a.shaftwidth,
        height=a.shaftwidth,
        color=a.color,
        frame=a.frame,
        visible=0,
    )
    m2 = export_box(abox)
    m2 = add_texture(a, m2)
    del abox
    # concatenate pyramid & box
    object_code = m1 + m2
    return object_code


def export_cone(a):
    cone_template = """
cone {
    <%(posx)f, %(posy)f, %(posz)f>, %(radius)f
    <%(pos2x)f, %(pos2y)f, %(pos2z)f>, %(minorradius)f
    pigment { color rgb <%(red)f, %(green)f, %(blue)f> }
}
"""
    pos2 = a.pos + a.axis
    object_code = cone_template % {
        "radius": a.radius,
        "minorradius": 0.0,
        "posx": a.x,
        "posy": a.y,
        "posz": a.z,
        "pos2x": pos2.x,
        "pos2y": pos2.y,
        "pos2z": pos2.z,
        "red": a.red,
        "green": a.green,
        "blue": a.blue,
    }
    object_code = process_frame(a, object_code)
    object_code = add_texture(a, object_code)
    return object_code


def export(
    display=None,
    filename=None,
    include_list=None,
    xy_ratio=4.0 / 3.0,
    custom_text="",
    shadowless=0,
):
    if display == None:  # no display specified so find active display
        dummy = sphere(visible=0)
        display = dummy.display
        del dummy

    if filename == None:
        filename = display.title + ".pov"

    if include_list == None:
        include_text = ""
    else:
        include_text = "\n"
        for x in include_list:
            include_text = include_text + '#include "' + x + '"\n'

    initial_comment = """// povray code generated by povexport.py
"""

    pyramid_def = """
// Four-sided pyramid from shapes2.inc, slightly modified.
#declare Pyramid = union {
    triangle { <-1, 0, -1>, <+1, 0, -1>, <0, 1, 0> }
    triangle { <+1, 0, -1>, <+1, 0, +1>, <0, 1, 0> }
    triangle { <-1, 0, +1>, <+1, 0, +1>, <0, 1, 0> }
    triangle { <-1, 0, +1>, <-1, 0, -1>, <0, 1, 0> }
    triangle { <-1, 0, -1>, <-1, 0, +1>, <1, 0, 1> }
    triangle { <-1, 0, -1>, <+1, 0, -1>, <1, 0, 1> }
    scale <.5, 1, .5>        // so height = width = 1
}
"""

    ambient_template = """
global_settings { ambient_light rgb <%(amb)f, %(amb)f, %(amb)f> }
"""

    background_template = """
background { color rgb <%(red)f, %(green)f, %(blue)f> }
"""

    light_template = """
light_source { <%(posx)f, %(posy)f, %(posz)f>
    color rgb <%(int)f, %(int)f, %(int)f>
}
"""

    camera_template = """
camera {
    right <-%(xyratio)f, 0, 0>      //visual uses right-handed coord. system
    location <%(posx)f, %(posy)f, %(posz)f>
    sky <%(upx)f, %(upy)f, %(upz)f>
    look_at <%(pos2x)f, %(pos2y)f, %(pos2z)f>
    angle %(fov)f
    rotate <0, 0, 0>
}
"""

    # begin povray setup
    file = open(filename, "wt")

    file.write(initial_comment + include_text + custom_text + pyramid_def)
    file.write(ambient_template % {"amb": display.ambient * 10})
    file.write(
        background_template
        % {
            "red": display.background[0],
            "green": display.background[1],
            "blue": display.background[2],
        }
    )

    # reproduce visual lighting (not ideal, but good approximation)
    for i in arange(len(display.lights)):
        light = display.lights[i]  # vector in direction of light
        intensity = mag(light)  # intensity of light (all lights are white)
        # far away to simulate parallel light
        pos = norm(light) * max(display.range) * 100.0
        light_code = light_template % {
            "posx": pos.x,
            "posy": pos.y,
            "posz": pos.z,
            "int": intensity * 5 / 3.0,
        }
        if shadowless:
            # insert frame_code at end (these rot's must be done last)
            end = rfind(light_code, "}")
            light_code = light_code[:end] + "    shadowless\n" + light_code[end:]

        file.write(light_code)

    cpos = display.mouse.camera
    ctr = display.center
    cup = display.up
    file.write(
        camera_template
        % {
            "xyratio": xy_ratio,
            "posx": cpos.x,
            "posy": cpos.y,
            "posz": cpos.z,
            "upx": cup.x,
            "upy": cup.y,
            "upz": cup.z,
            "pos2x": ctr.x,
            "pos2y": ctr.y,
            "pos2z": ctr.z,
            "fov": display.fov * 180 / pi,
        }
    )

    for obj in display.objects:
        key = obj.__class__
        if key in legal:
            obj_name = legal[key]
            if obj_name != "frame":
                function_name = "export_" + obj_name
                function = globals().get(function_name)
                object_code = function(obj)
                file.write(object_code)
        else:
            print("WARNING: export function for " + obj_name + " not implemented")

    file.close()
    return (
        "The export() function no longer returns the scene as an\n"
        "endless POV-Ray string, but saves it to a file instead."
    )


if __name__ == "__main__":
    print(__doc__)

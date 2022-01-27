#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""object_to_image

Loads a serialized graph object in memory and generates an PNG image.
"""

__author__ = "Jerome Hussenet, Cedric Bonhomme"
__version__ = "$Revision: 0.2 $"
__date__ = "$Date: 2012/02/05 $"
__copyright__ = (
    "Copyright (c) 2010-2012 Jerome Hussenet, Copyright (c) 2010-2012 Cedric Bonhomme"
)
__license__ = "GNU General Public License v3 or later (GPLv3+)"

from PIL import Image, ImageDraw, ImageFont

import pickle
import math

size = 1100  # 300
ip_radius = 470  # 140
port_radius = 420  # 130
port_d_radius = 420  # 130
link_radius = 390  # 130
xc, yc = size / 2, size / 2


def color():
    colors = (
        ("#ff9900", "#ffcc99"),
        ("#0000ff", "#9999ff"),
        ("#00ff00", "#99ff99"),
        ("#ff0000", "#ff9999"),
        ("#ffff00", "#ffff99"),
        ("#9900ff", "#9999ff"),
        ("#6699ff", "#66ffff"),
    )
    while 1:
        for i in colors:
            yield i


def rotate_text(image, position, txt, anglerot, color):
    """
    Rotates a text.
    """
    font = ImageFont.load_default()
    imtmp = Image.new("RGBA", font.getsize(txt))
    drawtmp = ImageDraw.Draw(imtmp)
    drawtmp.text((0, 0), txt, font=font, fill=color)
    imtmp2 = imtmp.rotate(anglerot * -1, expand=1)
    w, h = imtmp2.size
    x, y = position[0], position[1]
    if anglerot >= 0 and anglerot < 90:
        pass
    if anglerot >= 90 and anglerot < 180:
        x -= w
    if anglerot >= 180 and anglerot < 270:
        x -= w
        y -= h
    if anglerot >= 270 and anglerot < 360:
        y -= h
    image.paste(imtmp2, (x, y), mask=imtmp2)
    del drawtmp


def circular_arc(x_c, y_c, r, ang1, ang2, draw, color):
    """
    Creates a circular arc.
    """
    rang1, rang2 = math.radians(ang1), math.radians(ang2)
    x1, y1 = x_c + r * math.cos(rang1), y_c + r * math.sin(rang1)
    x2, y2 = x_c + r * math.cos(rang2), y_c + r * math.sin(rang2)
    # draw.line((x_c, y_c, x1, y1), fill="black")
    # draw.line((x_c, y_c, x2, y2), fill="black")
    # print x1, y1, ang1, rang1
    # print x2, y2, ang2, rang2

    x = 0
    y = r
    m = 5 - 4 * r

    while x <= y:
        cur_ang = math.degrees(math.atan2(y, x))
        if ang1 <= 90 - cur_ang and ang2 >= 90 - cur_ang:
            draw.point((x_c + y, y_c + x), fill=color)  # 0-45
        if ang1 <= cur_ang and ang2 >= cur_ang:
            draw.point((x_c + x, y_c + y), fill=color)  # 45-90
        if ang1 <= 180 - cur_ang and ang2 >= 180 - cur_ang:
            draw.point((x_c - x, y_c + y), fill=color)  # 90-135
        if ang1 <= 90 + cur_ang and ang2 >= 90 + cur_ang:
            draw.point((x_c - y, y_c + x), fill=color)  # 135-180
        if ang1 <= 270 - cur_ang and ang2 >= 270 - cur_ang:
            draw.point((x_c - y, y_c - x), fill=color)  # 180-225
        if ang1 <= 180 + cur_ang and ang2 >= 180 + cur_ang:
            draw.point((x_c - x, y_c - y), fill=color)  # 225-270
        if ang1 <= 360 - cur_ang and ang2 >= 360 - cur_ang:
            draw.point((x_c + x, y_c - y), fill=color)  # 270-315
        if ang1 <= 270 + cur_ang and ang2 >= 270 + cur_ang:
            draw.point((x_c + y, y_c - x), fill=color)  # 315-360

        if m > 0:
            y = y - 1
            m = m - 8 * y
        x = x + 1
        m = m + 8 * x + 4

    return (x1, y1, x2, y2)


def make_bezier(xys):
    """
    xys should be a sequence of 2-tuples (Bezier control points)
    from http://stackoverflow.com/questions/246525/how-can-i-draw-a-bezier-curve-using-pythons-pil
    """
    n = len(xys)
    combinations = pascal_row(n - 1)

    def bezier(ts):
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t ** i for i in range(n))
            upowers = reversed([(1 - t) ** i for i in range(n)])
            coefs = [c * a * b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                tuple(
                    sum([coef * p for coef, p in zip(coefs, ps)])
                    for ps in list(zip(*xys))
                )
            )
        return result

    return bezier


def pascal_row(n):
    """
    This returns the nth row of Pascal's Triangle
    from http://stackoverflow.com/questions/246525/how-can-i-draw-a-bezier-curve-using-pythons-pil
    """
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n // 2 + 1):
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n & 1 == 0:
        # n is even
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result))
    return result


def object_to_image(obj_file, image_file):

    if options.verbose:
        print("Loading objet...")
    dic_obj = open(obj_file, "rb")
    dic_link = pickle.load(dic_obj)

    # print dic_link
    if options.verbose:
        print("Generate Communication stats...")

    dic_stat = {}
    num_total = 0
    for ip_src in dic_link:
        if ip_src not in dic_stat:
            dic_stat[ip_src] = {}
            dic_stat[ip_src]["out"] = {}
            dic_stat[ip_src]["in"] = {}
        for ip_dst in dic_link[ip_src]:
            if ip_dst not in dic_stat:
                dic_stat[ip_dst] = {}
                dic_stat[ip_dst]["out"] = {}
                dic_stat[ip_dst]["in"] = {}
            for port_src in dic_link[ip_src][ip_dst]:
                for port_dst in dic_link[ip_src][ip_dst][port_src]:
                    num = dic_link[ip_src][ip_dst][port_src][port_dst]
                    num_total += num
                    dic_stat[ip_src]["out"][port_src] = (
                        dic_stat[ip_src]["out"].get(port_src, 0) + num
                    )
                    dic_stat[ip_dst]["in"][port_dst] = (
                        dic_stat[ip_dst]["in"].get(port_dst, 0) + num
                    )

    if options.verbose:
        print("Number of communication: ", num_total)
        print("Number of IPs: ", len(dic_stat))

    dic_info = {"ip": {}, "port": {}}

    im = Image.new("RGBA", (size, size))  # transparent
    # im = Image.new("RGB", (size,size), "white")

    draw = ImageDraw.Draw(im)
    # draw.line((0, 0) + im.size, fill=128)
    # draw.line((0, im.size[1], im.size[0], 0), fill=128)
    last_angle = 0
    color_gen = color()
    if options.verbose:
        print("Draw IP and Ports circles...")
    for ip in dic_stat:  # draw ip circle
        num_out = 0
        num_in = 0
        port_list = []
        for port in dic_stat[ip]["in"]:
            num_in += dic_stat[ip]["in"][port]
            if port not in port_list:
                port_list.append(port)
        for port in dic_stat[ip]["out"]:
            num_out += dic_stat[ip]["out"][port]
            if port not in port_list:
                port_list.append(port)

        angle = ((num_out + num_in) * 360.0) / (num_total * 2.0)

        last_angle2 = last_angle
        color_gen2 = color()
        for port in port_list:
            port_num_in = dic_stat[ip]["in"].get(port, 0)
            port_num_out = dic_stat[ip]["out"].get(port, 0)
            angle2i = (port_num_in * angle) / (num_out + num_in)
            angle2o = (port_num_out * angle) / (num_out + num_in)
            angle2 = angle2i + angle2o

            cur_color2 = next(color_gen2)

            # print port, port_num_out+port_num_in, last_angle2, last_angle2+angle2, cur_color2
            (xps, yps, xpe, ype) = circular_arc(
                xc,
                yc,
                port_radius,
                last_angle2,
                last_angle2 + angle2,
                draw,
                cur_color2[0],
            )
            x2, y2 = xc + port_radius * math.cos(
                math.radians(last_angle2 + angle2 / 2)
            ), yc + port_radius * math.sin(math.radians(last_angle2 + angle2 / 2))

            # draw.text((x2,y2), str(port), fill=cur_color2[0])
            rotate_text(
                im,
                (int(x2), int(y2)),
                str(port),
                int(round(last_angle2 + angle2 / 2)),
                cur_color2[0],
            )

            angtmpps = math.atan2(yps - yc, xps - xc)
            angtmppe = math.atan2(ype - yc, xpe - xc)
            xtmpps, ytmpps = xc + link_radius * math.cos(
                angtmpps
            ), yc + link_radius * math.sin(angtmpps)
            xtmppe, ytmppe = xc + link_radius * math.cos(
                angtmppe
            ), yc + link_radius * math.sin(angtmppe)
            draw.line((xps, yps, xtmpps, ytmpps), fill="black")
            draw.line((xpe, ype, xtmppe, ytmppe), fill="black")

            (xis, yis, xie, yie) = circular_arc(
                xc,
                yc,
                port_d_radius,
                last_angle2,
                last_angle2 + angle2i,
                draw,
                cur_color2[1],
            )
            (xos, yos, xoe, yoe) = circular_arc(
                xc,
                yc,
                port_d_radius,
                last_angle2 + angle2i,
                last_angle2 + angle2,
                draw,
                cur_color2[0],
            )
            xt1, yt1 = xc + port_d_radius * math.cos(
                math.radians(last_angle2 + angle2i / 2)
            ), xc + port_d_radius * math.sin(math.radians(last_angle2 + angle2i / 2))
            xt2, yt2 = xc + port_d_radius * math.cos(
                math.radians(last_angle2 + angle2i + angle2o / 2)
            ), xc + port_d_radius * math.sin(
                math.radians(last_angle2 + angle2i + angle2o / 2)
            )

            angtmpis = math.atan2(yis - yc, xis - xc)
            angtmpie = math.atan2(yie - yc, xie - xc)
            angtmpos = math.atan2(yos - yc, xos - xc)
            angtmpoe = math.atan2(yoe - yc, xoe - xc)
            xtmpis, ytmpis = xc + link_radius * math.cos(
                angtmpis
            ), yc + link_radius * math.sin(angtmpis)
            xtmpie, ytmpie = xc + link_radius * math.cos(
                angtmpie
            ), yc + link_radius * math.sin(angtmpie)
            xtmpos, ytmpos = xc + link_radius * math.cos(
                angtmpos
            ), yc + link_radius * math.sin(angtmpos)
            xtmpoe, ytmpoe = xc + link_radius * math.cos(
                angtmpoe
            ), yc + link_radius * math.sin(angtmpoe)
            draw.line((xis, yis, xtmpis, ytmpis), fill="black")
            draw.line((xos, yos, xtmpos, ytmpos), fill="black")
            draw.line((xie, yie, xtmpie, ytmpie), fill="black")
            draw.line((xoe, yoe, xtmpoe, ytmpoe), fill="black")

            # draw.text((xt1,yt1), "in", fill=cur_color2[1])
            # draw.text((xt2,yt2), "out", fill=cur_color2[0])
            if port_num_in > 0:
                rotate_text(
                    im,
                    (int(xt1), int(yt1)),
                    "in",
                    int(round(last_angle2 + angle2i / 2)),
                    cur_color2[1],
                )
            if port_num_out > 0:
                rotate_text(
                    im,
                    (int(xt2), int(yt2)),
                    "out",
                    int(round(last_angle2 + angle2 / 2)),
                    cur_color2[0],
                )

            key = ip + ":" + str(port)
            dic_info["port"][key] = {}
            dic_info["port"][key]["start"] = (xps, yps, last_angle2)
            dic_info["port"][key]["end"] = (xpe, ype, last_angle2 + angle2)
            dic_info["port"][key]["angle"] = angle2
            dic_info["port"][key]["starti"] = (xis, yis, last_angle2)
            dic_info["port"][key]["endi"] = (xie, yie, last_angle2 + angle2i)
            dic_info["port"][key]["anglei"] = angle2i
            dic_info["port"][key]["starto"] = (xos, yos, last_angle2 + angle2i)
            dic_info["port"][key]["endo"] = (xoe, yoe, last_angle2 + angle2i + angle2o)
            dic_info["port"][key]["angleo"] = angle2o
            dic_info["port"][key]["num_in"] = port_num_in
            dic_info["port"][key]["num_out"] = port_num_out
            dic_info["port"][key]["color"] = cur_color2
            dic_info["port"][key]["linki"] = {}
            dic_info["port"][key]["linko"] = {}

            last_angle2 += angle2

        cur_color = next(color_gen)
        # print ip, num_out+num_in, last_angle, last_angle+angle, cur_color

        # xcp, ycp = xc + 20 * math.cos(math.radians(last_angle+angle/2)), yc + 20 * math.sin(math.radians(last_angle+angle/2))

        (xs, ys, xe, ye) = circular_arc(
            xc, yc, ip_radius, last_angle, last_angle + angle, draw, cur_color[0]
        )

        dic_info["ip"][ip] = {}
        dic_info["ip"][ip]["start"] = (xs, ys)
        dic_info["ip"][ip]["end"] = (xe, ye)
        dic_info["ip"][ip]["angle"] = angle
        dic_info["ip"][ip]["num_in"] = num_in
        dic_info["ip"][ip]["num_out"] = num_out
        dic_info["ip"][ip]["color"] = cur_color

        angtmps = math.atan2(ys - yc, xs - xc)
        angtmpe = math.atan2(ye - yc, xe - xc)
        xtmps, ytmps = xc + link_radius * math.cos(
            angtmps
        ), yc + link_radius * math.sin(angtmps)
        xtmpe, ytmpe = xc + link_radius * math.cos(
            angtmpe
        ), yc + link_radius * math.sin(angtmpe)
        draw.line((xs, ys, xtmps, ytmps), fill="black")
        draw.line((xe, ye, xtmpe, ytmpe), fill="black")

        x, y = xc + ip_radius * math.cos(
            math.radians(last_angle + angle / 2)
        ), xc + ip_radius * math.sin(math.radians(last_angle + angle / 2))
        # draw.text((x,y), ip, fill=cur_color[0])
        # print last_angle+angle/2, ip
        rotate_text(
            im, (int(x), int(y)), ip, int(round(last_angle + angle / 2)), cur_color[0]
        )
        last_angle += angle

    # at this point, the circle is drawn
    # now, let's go for the link
    if options.verbose:
        print("Generate Port communication list...")
    # this loop prepares the link calculation by giving for each port a list of in a out communication
    for ip_src in dic_link:
        for ip_dst in dic_link[ip_src]:
            for port_src in dic_link[ip_src][ip_dst]:
                for port_dst in dic_link[ip_src][ip_dst][port_src]:
                    key1 = ip_src + ":" + str(port_src)
                    key2 = ip_dst + ":" + str(port_dst)
                    dic_info["port"][key2]["linki"][key1] = {}
                    dic_info["port"][key2]["linki"][key1]["weight"] = dic_link[ip_src][
                        ip_dst
                    ][port_src][port_dst]
                    dic_info["port"][key1]["linko"][key2] = {}
                    dic_info["port"][key1]["linko"][key2]["weight"] = dic_link[ip_src][
                        ip_dst
                    ][port_src][port_dst]

    # this loop draws the sub arc of "connected" port
    for key in dic_info["port"]:
        ip, port = key.split(":")

        # for the entering link
        last_angle = dic_info["port"][key]["starti"][2]
        for key2 in dic_info["port"][key]["linki"]:
            anglei = dic_info["port"][key]["anglei"]
            num_in = dic_info["port"][key]["num_in"]
            weight = dic_info["port"][key]["linki"][key2]["weight"]
            angle = (anglei * weight) / num_in
            cur_color = dic_info["port"][key2]["color"][0]
            (xs, ys, xe, ye) = circular_arc(
                xc, yc, link_radius, last_angle, last_angle + angle, draw, cur_color
            )
            dic_info["port"][key]["linki"][key2]["start"] = (xs, ys, last_angle)
            dic_info["port"][key]["linki"][key2]["end"] = (xe, ye, last_angle + angle)
            x, y = xc + link_radius * math.cos(
                math.radians(last_angle + angle / 2)
            ), xc + link_radius * math.sin(math.radians(last_angle + angle / 2))
            # draw.text((x,y), key2, fill=cur_color)
            kip, kport = key2.split(":")
            rotate_text(
                im,
                (int(x), int(y)),
                kport,
                int(round(last_angle + angle / 2)),
                cur_color,
            )
            last_angle += angle

        # for the leaving link
        last_angle = dic_info["port"][key]["starto"][2]
        for key2 in dic_info["port"][key]["linko"]:
            angleo = dic_info["port"][key]["angleo"]
            num_out = dic_info["port"][key]["num_out"]
            weight = dic_info["port"][key]["linko"][key2]["weight"]
            angle = (angleo * weight) / num_out
            cur_color = dic_info["port"][key]["color"][0]
            (xs, ys, xe, ye) = circular_arc(
                xc, yc, link_radius, last_angle, last_angle + angle, draw, cur_color
            )
            dic_info["port"][key]["linko"][key2]["start"] = (xs, ys, last_angle)
            dic_info["port"][key]["linko"][key2]["end"] = (xe, ye, last_angle + angle)
            x, y = xc + link_radius * math.cos(
                math.radians(last_angle + angle / 2)
            ), xc + link_radius * math.sin(math.radians(last_angle + angle / 2))
            # draw.text((x,y), key2, fill=cur_color)
            kip, kport = key2.split(":")
            rotate_text(
                im,
                (int(x), int(y)),
                kport,
                int(round(last_angle + angle / 2)),
                cur_color,
            )
            last_angle += angle

    if options.verbose:
        print("Draw Communication Links...")
    # Now, let's draw the links :)
    for ip_src in dic_link:
        for ip_dst in dic_link[ip_src]:
            for port_src in dic_link[ip_src][ip_dst]:
                for port_dst in dic_link[ip_src][ip_dst][port_src]:
                    """
                    Bezier Curve Version
                    """
                    keyi = ip_dst + ":" + str(port_dst)
                    keyo = ip_src + ":" + str(port_src)
                    starto = dic_info["port"][keyo]["linko"][keyi]["start"]
                    endo = dic_info["port"][keyo]["linko"][keyi]["end"]
                    starti = dic_info["port"][keyi]["linki"][keyo]["start"]
                    endi = dic_info["port"][keyi]["linki"][keyo]["end"]
                    angleo = dic_info["port"][keyo]["angleo"]
                    anglei = dic_info["port"][keyi]["anglei"]
                    dang1 = (angleo - anglei) % 360
                    dang2 = (anglei - angleo) % 360
                    if dang1 < dang2:
                        midang = (angleo - dang1 / 2) % 360
                    else:
                        midang = (anglei - dang2 / 2) % 360
                    # print dang1, dang2, midang
                    xcc, ycc = (
                        0.5 * link_radius * math.cos(math.radians(midang)) + size / 2,
                        0.5 * link_radius * math.sin(math.radians(midang)) + size / 2,
                    )

                    ts = [t / 100.0 for t in range(101)]
                    # points1 = [(starti[0],starti[1]),(xcc,ycc),(starto[0],starto[1])]
                    points1 = [(starti[0], starti[1]), (xcc, ycc), (endo[0], endo[1])]
                    bezier = make_bezier(points1)
                    pts1 = bezier(ts)
                    # points2 = [(endo[0],endo[1]),(xcc,ycc),(endi[0],endi[1])]
                    points2 = [(starto[0], starto[1]), (xcc, ycc), (endi[0], endi[1])]
                    bezier = make_bezier(points2)
                    pts2 = bezier(ts)
                    cur_color = dic_info["port"][keyo]["color"][0]

                    draw.polygon(pts1 + pts2, fill=cur_color)
                    draw.line(pts2 + pts1, fill="black")

                    """
                    Circular Arc version
                    """
                    """
                    keyi = ip_dst+":"+str(port_dst)
                    keyo = ip_src+":"+str(port_src)
                    starto = dic_info["port"][keyo]["linko"][keyi]["start"]
                    endo = dic_info["port"][keyo]["linko"][keyi]["end"]
                    starti = dic_info["port"][keyi]["linki"][keyo]["start"]
                    endi = dic_info["port"][keyi]["linki"][keyo]["end"]
                    xc1, yc1 = (starto[0]+endi[0])/2,(starto[1]+endi[1])/2
                    xc2, yc2 = (starti[0]+endo[0])/2,(starti[1]+endo[1])/2
                    radius1 = math.sqrt((starto[0]-endi[0])**2+(starto[1]-endi[1])**2)/2
                    radius2 = math.sqrt((starti[0]-endo[0])**2+(starti[1]-endo[1])**2)/2
                    rang1 = math.atan2(starto[1]-yc1, starto[0]-xc1)
                    rang2 = math.atan2(starti[1]-yc2, starti[0]-xc2)
                    if rang1<0:
                        rang1 = 3.14+rang1
                    if rang2<0:
                        rang2 = 3.14+rang2
                    ang1 = math.degrees(rang1)
                    ang2 = math.degrees(rang2)
                    cur_color = dic_info["port"][keyo]["color"][0]
                    #print ip_src, ip_dst, port_src, port_dst
                    print xc1, yc1, xc2, yc2, rang1, ":", ang1, rang2, ":", ang2, radius1, radius2

                    circular_arc(xc1, yc1, radius1, ang1, ang1+180, draw, cur_color)
                    circular_arc(xc2, yc2, radius2, ang2, ang2+180, draw, cur_color)

                    #draw.line((starto[0],starto[1],endi[0],endi[1]), fill=cur_color)
                    #draw.line((endo[0],endo[1],starti[0],starti[1]), fill=cur_color)
                    """

    del draw
    # print dic_info
    im.save(image_file, "png")


if __name__ == "__main__":
    # Point of entry in execution mode.
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="obj_file", help="Python serialized object")
    parser.add_option("-o", "--output", dest="image_file", help="Image file")
    parser.add_option(
        "-q",
        "--quiet",
        action="store_false",
        dest="verbose",
        help="be vewwy quiet (I'm hunting wabbits)",
    )
    parser.set_defaults(
        obj_file="./data/dic.pyobj", image_file="./data/ip.png", verbose=True
    )

    (options, args) = parser.parse_args()

    object_to_image(options.obj_file, options.image_file)

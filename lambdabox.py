import pyglet, math
from pyglet.gl import *
import shader
from triangle import Triangle

class vec2:

    def __init__(self, *args):
        """Takes coordinates either as a tuple or separate"""
        self.set(args)

    def set(self, *args):
        """Takes coordinates either as a tuple or separate"""
        if len(args) == 1:
            arg = args[0]
            self.x = float(arg[0])
            self.y = float(arg[1])
        elif len(args) == 2:
            self.x = float(args[0])
            self.y = float(args[1])
        else:
            raise TypeError("vec2.__init__() takes either one or two arguments; "+len(args)+" given.")

    def coords(self):
        return self.x, self.y

    def __add__(self, other):
        if type(other) == type(self):
            print "Hello"
            t = vec2(self.x+other.x, self.y+other.y)
            return None
        else:
            raise TypeError

    def __sub__(self, other):
        if type(other) == type(self):
            return vec2(self.x-other.x, self.y-other.y)
        else:
            raise TypeError

    def __mul__(self, other):
        if type(other) == type(self):
            return self.x*other.x+self.y*other.y
        elif type(other) == float or type(other) == int:
            return vec2(self.x*other, self.y*other)

    def __repr__(self):
        return "vec2 ("+str(self.x)+", "+str(self.y)+")"

    def __getitem__(self, i):
        if i == 0:
            return self.x
        elif i == 1:
            return self.y

class Box:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lines = []#Lines this box is connected to
        self.triangleconstant = math.tan(math.pi/8)/(math.tan(math.pi/8)+1)
        self.calc_s1_s2(48)
        self.update(x, y)

    def calc_s1_s2(self, width):
        """s1 and s2 are lengths for calculating the corner coordinates from the center one"""
        self.s1 = width*self.triangleconstant
        self.s2 = width-self.s1

    def point_in_triangle(self, p, a, b, x, y):
        """p: position vector to a and b; a, b: vectors defining the triangle; x, y: coordinates of the point"""
        ax, ay = a.coords()
        ax = float(ax); ay = float(ay)
        bx, by = b.coords()
        bx = float(bx); by = float(by)
        px = x-p[0]#do some conversion to port the mouse coordinates into a coordinate system based on the tip of the triangle
        py = y-p[1]
        r = (-py*bx/by+px)/(-ay*bx/by+ax)#calculate r and s values to represent the point by a and b
        s = (px-r*ax)/bx
        if r<1 and r>0 and s<1 and s>0 and (r+s)<1 and (r+s)>0:#standard point-in-triangle test
            return True
        else:
            return False

    def update(self, x, y):
        self.x = x
        self.y = y
        self.batch = pyglet.graphics.Batch()

    def click(self, x, y):
        if self.gethover(x, y):
            set_drag(self)

class AbstractorBox(Box):

    def __init__(self, x, y):
        self.topline = None
        self.rightline = None
        self.bottomline = None
        self.color = (1.0, 0.4, 0.8)
        Box.__init__(self, x, y)
        
    def get_vertices(self, centerx, centery):
        left = centerx-self.s2
        right = centerx+self.s1
        bottom = centery-self.s2
        top = centery+self.s1
        return vec2(right, bottom), vec2(right, top), vec2(left, top)

    def update(self, x, y):
        Box.update(self, x, y)
        self.a, self.b, self.c = a, b, c = self.get_vertices(x, y)
        pos = vec2(x, y)
        self.leftattach = (b.x, y)
        self.bottomattach = (x, b.y)
        self.rightattach = (x+self.s1, y+self.s1)
        self.right_triangle = Triangle(a, b, pos, self.color, self.batch)
        self.top_triangle = Triangle(b, c, pos, self.color, self.batch)
        self.bottom_triangle = Triangle(c, a, pos, self.color, self.batch)
        self.glow = self.batch.add_indexed(6, pyglet.gl.GL_TRIANGLES, None, [0, 1, 3, 1, 4, 3, 1, 2, 4, 2, 5, 4, 2, 0, 5, 0, 3, 5],
                ('v2f', (a.x+255, a.y-512 , b.x+255, b.y+255, c.x-512, c.y+255, a.x, a.y, b.x, b.y, c.x, c.y)),
                ('c4f', (self.color+(0.0,))*3+(self.color+(1.0,))*3)
                )
        self.topattach = (x, a.y)
        self.bottomattach = (x-self.s1, y-self.s1)
        self.rightattach = (a.x, y)

    def draw(self):
        self.batch.draw()

    def gethover(self, x, y):
        hovered = False
        if self.top_triangle.gethover(vec2(x, y)):
            hovered = self, self.leftattach
        if self.bottom_triangle.gethover(vec2(x, y)):
            hovered = self, self.bottomattach
        if self.right_triangle.gethover(vec2(x, y)):
            hovered = self, self.rightattach
        return hovered

    def drag_end(self, x, y):
        pass

class ApplicatorBox(Box):

    def __init__(self, x, y):
        self.leftline = None
        self.rightline = None
        self.bottomline = None
        self.color = (0.4, 1.0, 0.8)
        Box.__init__(self, x, y)
        
    def get_vertices(self, centerx, centery):
        left = centerx-self.s1
        right = centerx+self.s2
        bottom = centery-self.s1
        top = centery+self.s2
        return vec2(left, top), vec2(left, bottom), vec2(right, bottom)

    def update(self, x, y):
        Box.update(self, x, y)
        pos = vec2(x, y)
        self.a, self.b, self.c = a, b, c = self.get_vertices(x, y)
        self.left_triangle = Triangle(a, b, pos, self.color, self.batch)
        self.bottom_triangle = Triangle(b, c, pos, self.color, self.batch)
        self.right_triangle = Triangle(c, a, pos, self.color, self.batch)
        self.glow = self.batch.add_indexed(6, pyglet.gl.GL_TRIANGLES, None, [0, 1, 3, 1, 4, 3, 1, 2, 4, 2, 5, 4, 2, 0, 5, 0, 3, 5],
                ('v2f', (a.x-255, a.y+512 , b.x-255, b.y-255, c.x+512, c.y-255, a.x, a.y, b.x, b.y, c.x, c.y)),
                ('c4f', (self.color+(0.0,))*3+(self.color+(1.0,))*3)
                )
        self.leftattach = (b.x, y)
        self.bottomattach = (x, b.y)
        self.rightattach = (x+self.s1, y+self.s1)

    def draw(self):
        self.batch.draw()
        if self.rightline:
            self.rightline.draw()
        if self.leftline:
            self.leftline.draw()

    def gethover(self, x, y):
        hovered = False
        if x > self.a.x and x < self.c.x and y > self.b.y and y < self.a.y: #bounding box check
            if self.left_triangle.gethover(vec2(x, y)):
                hovered = self, self.leftattach
            if self.bottom_triangle.gethover(vec2(x, y)):
                hovered = self, self.bottomattach
            if self.right_triangle.gethover(vec2(x, y)):
                hovered = self, self.rightattach
        else:
            self.left_triangle.highlight(False)
            self.bottom_triangle.highlight(False)
            self.right_triangle.highlight(False)
        return hovered

    def gethover_recursive(self, x, y):
        hovered = self.gethover(x, y)
        if hovered:
            return hovered
        else:
            if self.rightline:
                rightline_hover = self.rightline.gethover_recursive(x, y)
                if rightline_hover:
                    return rightline_hover
                else:
                    if self.leftline:
                        leftline_hover = self.leftline.gethover_recursive(x, y)
                        if leftline_hover:
                            return leftline_hover
                        else:
                            return False

    def drag_end(self, x, y):
        pass

class Mulplicator:

    def __init__(self, x, y, source):
        self.halfwidth = 8
        self.update(x, y)
        self.source = source
        self.sinks = []

    def update(self, x, y):
        self.x, self.y = x, y
        left = x-self.halfwidth
        right = x+self.halfwidth
        bottom = y-self.halfwidth
        top = y+self.halfwidth
        self.batch = pyglet.graphics.Batch()
        self.square = self.batch.add_indexed(4, pyglet.gl.GL_TRIANGLES, None, [0, 1, 2, 0, 2, 3],
                ('v2f', (left, y, x, bottom, right, y, x, top)),
                ('c4f', (0.5, 0.4, 1.0, 1.0)*4)
                )
        self.glow = self.batch.add_indexed(8, pyglet.gl.GL_TRIANGLES, None, [0, 1, 4, 4, 5, 1, 1, 2, 5, 5, 6, 2, 2, 3, 6, 6, 7, 3, 3, 0, 7, 7, 4, 0],
                ('v2f', (left-256, y, x, bottom-256, right+256, y, x, top+256, left, y, x, bottom, right, y, x, top)),
                ('c4f', (0.5, 0.4, 1.0, 0.0)*4+(0.5, 0.4, 1.0, 1.0)*4)
                )

    def draw(self):
        self.batch.draw()

    def drag_end(self, x, y):
        pass

    def checkhover(self, x, y):
        pass

class Line:

    def __init__(self, inpoint, outpoint):
        self.inpoint = inpoint
        self.outpoint = outpoint
        self.endbox = None

    def update_start(self, x, y):
        self.sx = x
        self.sy = y

    def update_end(self, x, y):
        self.ex = x
        self.ey = y

    def update(self, x, y):
        self.update_end(x, y)

    def drag_end(self, x, y):
        self.endbox = Mulplicator(x, y, self)

    def draw(self):
        if self.endbox:
            self.endbox.draw()
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
                ('v2i', (self.sx, self.sy, self.ex, self.ey)),
                ('c3f', (1.0,)*6)
                )

    def hover(self, state=False):
        if self.endbox:
            self.endbox.hover(state)

window = pyglet.window.Window()
pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
windowshader = shader.Shader(' '.join(open('vertexshader.glsl')), ' '.join(open('fragmentshader.glsl')))
fpsdisplay = pyglet.clock.ClockDisplay()
entities = pyglet.text.Label(text="0", font_size=18, font_name="Monospace", x=0, y=window.height, anchor_x="left", anchor_y="top")
boxes = []
drag = None

def set_drag(box):
    global drag
    drag = box

@window.event
def on_draw():
    window.clear()
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0., window.width, 0., window.height, 0., 1.)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    windowshader.bind()
    for box in boxes:
        box.draw()
    windowshader.unbind()
    fpsdisplay.draw()
    entities.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    for box in boxes:
        box.gethover(x, y)

@window.event
def on_mouse_press(x, y, button, modifier):
    global dragline
    global drag
    hover = None
    boxes.reverse()
    for box in boxes:
        hover = box.gethover(x, y)
        if hover:
            break
    boxes.reverse()
    if hover:
        drag = hover[0]
        if button == pyglet.window.mouse.LEFT:
            dragline = False
        elif button == pyglet.window.mouse.RIGHT:
            attachpoint = hover[1]
            if attachpoint:
                line = Line(attachpoint, (x, y))
                drag = line
    elif hover == None:
        if button == pyglet.window.mouse.LEFT:
            boxes.append(AbstractorBox(x, y))
        elif button == pyglet.window.mouse.RIGHT:
            boxes.append(ApplicatorBox(x, y))
        elif button == pyglet.window.mouse.MIDDLE:
            boxes.append(Mulplicator(x, y, None))
    entities.text = str(len(boxes))

@window.event
def on_mouse_release(x, y, button, modifier):
    global drag
    if drag:
        drag.drag_end(x, y)
        drag = None

@window.event
def on_mouse_drag(x, y, dx, dy, symbol, modifier):
    global drag
    if drag:
        drag.update(x, y)

@window.event
def on_key_press(symbol, modifiers):
    print drag

pyglet.app.run()

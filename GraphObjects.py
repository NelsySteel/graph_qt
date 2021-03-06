from types import NoneType
from typing import Any
from pygame import Vector2
from Utils import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QColorConstants, QInputEvent
from PyQt5.QtCore import Qt, QEvent
from random import choice as get_random
from math import ceil, floor, sqrt

colors = (
    '#e6ccff',
    '#9999ff',
    '#99c2ff',
    '#99ebff',
    '#66ffcc',
    '#98e698',
    '#dfbf9f',
    '#ffdd99',
    '#ffaa80',
    '#ffb3cc',
    '#df9fbf',
    '#c2c2d6',
    '#b3d9ff',
    '#dddddd',
    '#ff9999',
)

class GraphicsFigure:
    #renders figure on screen
    def Render(self, painter: QPainter): ...

    #offset is used to create "safe" area to allow clicking near figure
    #mainly used by link - clicking exactly on line is a pain
    def IsIntersectingPoint(self, point: Vector2d, offset = 0): ...

    #processes input (only mouse events for now)
    def ProcessInput(self, event:QInputEvent): ...

    #Geets hint text that will be displayed on hover
    def GetHint(self): ...
    
class Node(GraphicsFigure):
    height : int = 10
    width : int = height * 2
    def __init__(self, parent):
        #top-left corner coordinates
        self.pos:Vector2d = Vector2d(0, 0)
        self.parent = parent #parent graph

        self.color = get_random(colors)

        #movement variables
        self.moving = False
        self.offset :Vector2d = None

    def GetHint(self):
        return 'Drag LMB to drag node\nDrag RMB to create link\nPress middle mouse button to Remove'    

    def Render(self, painter: QPainter):
        painter.save()
        col = QColor(0, 0, 0)
        col.setNamedColor(self.color)
        painter.setPen(col)

        painter.setBrush(col)
        painter.drawRect(self.pos.x, self.pos.y, self.width, self.height)
        painter.restore()
    
    def ProcessInput(self, event : QInputEvent):
        result = False
        type = event.type()
        mousePos = Vector2d(event.localPos().x(), event.localPos().y())
        max_x = self.parent.parent.width()
        max_y = self.parent.parent.height()
        mousePos.x = ClampInt(mousePos.x, 0, max_x)
        mousePos.y = ClampInt(mousePos.y, 0, max_y)
        if type == QEvent.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                #start moving
                if self.IsIntersectingPoint(mousePos):
                    self.moving = True
                    self.original_pos = self.pos.Clone()
                    center = self.GetCenter()
                    self.offset = center - mousePos
                    self.prev_mouse_pos = mousePos
                    result = True
        elif type == QEvent.MouseMove:
            if event.button() == Qt.MouseButton.NoButton:
                #update position
                if self.moving:
                    prev_valid_pos = self.pos.Clone()
                    old_center = self.GetCenter()

                    #trying to place where mouse is
                    new_position = mousePos + self.offset
                    self.MoveCenterTo(new_position.x, new_position.y)
                    
                    if not self.parent.IsValidNodePosition(self):
                        #intersection happened, trying to move towards mouse
                        diff = mousePos - self.prev_mouse_pos
                        new_center = old_center + diff
                        self.MoveCenterTo(new_center.x, new_center.y)
                        if not self.parent.IsValidNodePosition(self):
                            #still intersection, not moving
                            self.pos = prev_valid_pos
                    self.prev_mouse_pos = mousePos
                    result = True
        elif type == QEvent.MouseButtonRelease:
            if event.button() == Qt.MouseButton.LeftButton:
                #end moving
                if self.moving:
                    self.parent.UpdateNodeGrid(self, self.original_pos)
                    self.moving = False
                    self.offset = None
                    self.original_pos = None
                    result = True
        return result

    #offset is used to create "safe" area to allow clicking near figure
    #mainly used by link - clicking exactly on line is a pain
    def IsIntersectingPoint(self, point: Vector2d, offset = 0):
        isXInside = point.x > self.pos.x and point.x < self.pos.x + self.width
        isYInside = point.y > self.pos.y and point.y < self.pos.y + self.height
        return (isXInside and isYInside)

    #intersecting with another node
    def IsIntersectingOther(self, other):
        self_left = self.pos.x
        self_right = self.pos.x + self.width
        self_top = self.pos.y
        self_bottom = self.pos.y + self.height
        other_left = other.pos.x
        other_right = other.pos.x + other.width
        other_top = other.pos.y
        other_bottom = other.pos.y + other.height
        if self_left > other_right or self_right < other_left or self_top > other_bottom or self_bottom < other_top:
            return False
        return True

    def MoveCenterTo(self, newX, newY):
        self.pos.x = int(newX - self.width / 2)
        self.pos.y = int(newY - self.height / 2)
    
    def GetCenter(self):
        return Vector2d(self.pos.x + int(Node.width /2), self.pos.y + int(Node.height / 2))

    
class Link(GraphicsFigure):
    color = QColorConstants.Black
    def __init__(self, node1: Node, node2: Node = None):
        self.firstNode = node1
        self.secondNode = node2
        self.unfinished = node2 == None
        self.tempPoint = node1.GetCenter()

    def GetHint(self):
        return 'Press middle mouse button to Remove'
    
    def Render(self, painter: QPainter):
        painter.save()
        painter.setPen(self.color)
        start = self.GetStartPoint()         
        end = self.GetEndPoint()
        painter.drawLine(start.x, start.y, end.x, end.y)
        painter.restore()

    def ProcessInput(self, event : QInputEvent):
        result = False
        type = event.type()
        if type == QEvent.MouseMove:
            if self.unfinished:
                mousePos = event.localPos()
                self.UpdateTempPoint(mousePos.x(), mousePos.y())
                result = True
        return result

    def IsIntersectingPoint(self, point:Vector2d,  offset = 0):
        start = self.GetStartPoint()         
        end = self.GetEndPoint()
        x0, y0 = point.x, point.y
    
        AB = Vector2d(end.x - start.x, end.y - start.y)
        BA = Vector2d(start.x - end.x, start.y - end.y)
        AT = Vector2d(x0 - start.x, y0 - start.y)
        BT = Vector2d(x0 - end.x, y0 - end.y)

        #using scalar product to determing whether point normal to line exists
        if (AB.x * AT.x + AB.y *AT.y) < 0 or (BA.x * BT.x + BA.y * BT.y) < 0:
            #there is no normal to line, distance to closest end point
            distance_to_start = abs(sqrt((x0 - start.x) ** 2 + (y0 - start.y) ** 2)); 
            distance_to_end = abs(sqrt((x0 - end.x) ** 2 + (y0 - end.y) ** 2)); 
            distance = min(distance_to_start, distance_to_end)
        else:
            #distance to closest point on line
            length = sqrt((start.y - end.y) ** 2 + (end.x - start.x) ** 2)
            distance = abs(((start.y - end.y) * x0 + (end.x - start.x) * y0 + start.x * end.y - end.x * start.y) / length) 

        #takes "safe" area - offset - into account
        #to allow to click near the line
        return distance < offset

    def SetSecondNode(self, node : Node):
        self.secondNode = node
        self.unfinished = False

    def GetStartPoint(self):
        return self.firstNode.GetCenter()

    def GetEndPoint(self):
        if self.unfinished:
            return self.tempPoint
        return self.secondNode.GetCenter()

    def UpdateTempPoint(self, x, y):
        self.tempPoint = Vector2d(x, y)


#holds all objects and processes relative actions
class Graph:
    gridSize = Node.width * 2
    def __init__(self, parentWidget : QWidget):
        self.parent = parentWidget

        #order in this list influences render order
        self.objects: list[GraphicsFigure] = []

        #grid is used to optimize object intersection - only nearby nodes are checked
        #i didn't refactor self.objects - grid can in fact be used to store nodes, but it's used only for intersection
        #render and input processing still use self.objects
        #yeah, it influences app memory, but it doesn't influence performance and I didn't have time to refactor =)
        self.grid : dict[tuple[int, int], list[GraphicsFigure]] = {}

        #link which is in progress of creation
        #added to container after successfull creation
        self.currentLink:Link = None

    def GetNodeGrid(self, node:Node):
        x = node.pos.x // self.gridSize
        y = node.pos.y // self.gridSize
        return (x,y)

    def AddNode(self, node:Node):   
        #appending nodes to back so that links are always rendered first
        self.objects.append(node)
        cell = self.GetNodeGrid(node)
        if not cell in self.grid:
            self.grid[cell] = []
        self.grid[cell].append(node)

    def AddLink(self, link : Link):
        #appending links to front so that links are always rendered first
        self.objects.insert(0, link)

    def RemoveNode(self, node : Node):
        self.objects.remove(node)
        for object in self.objects[:]:
            if type(object) == Link:
                if object.firstNode == node or object.secondNode == node:
                    self.objects.remove(object)
        prev_cell = (node.pos.x // self.gridSize, node.pos.y // self.gridSize)
        if prev_cell in self.grid:
                self.grid[prev_cell].remove(node)
                if len(self.grid[prev_cell]) == 0:
                    self.grid.pop(prev_cell)

    def RemoveLink(self, link : Link):
        self.objects.remove(link)

    def RemoveObject(self, object:GraphicsFigure):
        if type(object) == Node:
            self.RemoveNode(object)    
        elif type(object) == Link:
            self.RemoveLink(object)

    def UpdateNodeGrid(self, node:Node, original_pos:Vector2d = Vector2d(-1, -1)):
        prev_cell = (original_pos.x // self.gridSize, original_pos.y // self.gridSize)
        new_cell = self.GetNodeGrid(node)
        if not new_cell in self.grid:
            self.grid[new_cell] = []
        if new_cell != prev_cell:
            #removing node from previous cell if it is valid (will be invalid for new nodes)
            #i remove empty cells to avoid checking them for intersection
            if prev_cell in self.grid:
                self.grid[prev_cell].remove(node)
                if len(self.grid[prev_cell]) == 0:
                    self.grid.pop(prev_cell)
            
            #moving node to new grid
            self.grid[new_cell].append(node)


    def GetObjectUnderMouse(self, mouse_pos:Vector2d, filter_type = None):
        #order is reversed in self.objects (for rendering)
        #so the items on top will be at the back!
        #reversed function is simply perfect - it doesn't create a copy, only reverses iterators. 
        # Love it.
        for object in reversed(self.objects):
            if filter_type == None or type(object) == filter_type:
                if object.IsIntersectingPoint(mouse_pos, 5):
                    return object

    def ShowHint(self, object: GraphicsFigure, mouse_pos:Vector2d, painter:QPainter):
        hint_text = object.GetHint()
        DrawTextFrame(hint_text, mouse_pos, painter)

    # renders visualization of objects grid on screen (just for hint)
    def RenderGrid(self, painter:QPainter):
        painter.setPen(QColorConstants.LightGray)
        x = 0
        y = 0
        while y < self.parent.height():
            painter.drawLine(0, y, self.parent.width(), y)
            y += Graph.gridSize

        while x < self.parent.width():
            painter.drawLine(x, 0, x, self.parent.height())
            x += Graph.gridSize 

    def RenderHint(self, painter:QPainter, mouse_pos:Vector2d):
        hint_object = self.GetObjectUnderMouse(mouse_pos)
        if hint_object:
            self.ShowHint(hint_object, mouse_pos, painter)

    def Render(self, painter: QPainter):
        for object in self.objects:
            object.Render(painter)
        if self.currentLink != None:
            self.currentLink.Render(painter)
    
    def ProcessIntersectionIsCell(self, node:Node, cell:tuple[int, int]):
        if cell in self.grid:
            for otherObject in self.grid[cell]:
                if otherObject != node:
                    if node.IsIntersectingOther(otherObject):
                        return True
            return False
    
    def IsValidNodePosition(self, node:Node):
        #edges
        if node.pos.x + node.width > self.parent.size().width() or node.pos.x < 0:
            return False

        if node.pos.y + node.height > self.parent.size().height() or node.pos.y < 0:
            return False

        #intersection with other nodes
        current_cell = self.GetNodeGrid(node)
        #check all 9 cells - the one in which thenode is and all it's neighbors
        for i in [current_cell[0] - 1, current_cell[0], current_cell[0]+1]:
            for j in [current_cell[1] - 1, current_cell[1], current_cell[1]+1]:
                if i>=0 and j>=0:   #valid cell index (left and top)
                    if i<= (self.parent.width() // Graph.gridSize) and j<= (self.parent.height() // Graph.gridSize):#valid cell index (bottom and right)
                        if self.ProcessIntersectionIsCell(node, (i, j)):
                            return False
        return True
        
    #check if link between two nodes (any order) exists        
    def IsLinkExists(self, node1 : Node, node2 : Node):
        for object in self.objects:
            if type(object) == Link:
                firstSame =            object.firstNode == node1
                secondEqualsFirst =    object.secondNode == node1
                firstEqualsSecond =    object.firstNode == node2
                secondSame =           object.secondNode == node2

                #There are no other possibble combinations
                if  (firstSame and secondSame) or (firstEqualsSecond and secondEqualsFirst):
                    return True
        return False

    def CreateNode(self, pos:Vector2d, isCenter = True):
        newNode = Node(self)
        if isCenter:
            newNode.MoveCenterTo(pos.x, pos.y)
        else:
            newNode.pos = pos

        if self.IsValidNodePosition(newNode):
            self.AddNode(newNode)
            return True
        return False

    def FillWindow(self):
        margin_size = Node.width//2
        margin = Vector2d(margin_size, margin_size)
        cell_size = Vector2d(Node.width + margin.x, Node.height + margin.y)
        window_width = self.parent.width()
        window_height = self.parent.height()

        cell_pos = Vector2d()

        while cell_pos.y<=window_height - Node.height:
            while cell_pos.x <= window_width - Node.width:
                self.CreateNode(cell_pos + margin, False)
                cell_pos.x += cell_size.x
            cell_pos.x = 0
            cell_pos.y += cell_size.y
                 

    def StartCreatingLink(self, mouse_pos : Vector2d):
        underlyiing_node = self.GetObjectUnderMouse(mouse_pos, Node)

        if underlyiing_node:
            self.currentLink = Link(underlyiing_node)

    def EndCreatingLink(self, mouse_pos : Vector2d):
        end_node = self.GetObjectUnderMouse(mouse_pos, Node)
        if end_node and end_node != self.currentLink.firstNode:
            if not self.IsLinkExists(self.currentLink.firstNode, end_node):
                self.currentLink.SetSecondNode(end_node)
                self.AddLink(self.currentLink)
        self.currentLink = None

    def ProcessInput(self, event : QInputEvent):
        result = False
        mousePos = Vector2d(event.localPos().x(), event.localPos().y())
        type = event.type()
        #processing all events that require knowledge about all objects
        if type == QEvent.MouseButtonDblClick:
            if event.button() == Qt.MouseButton.LeftButton:
                #creating new node
                result |= self.CreateNode(mousePos)
        
        elif type == QEvent.MouseButtonPress:
            #creating new link by dragging RMB
            if event.button() == Qt.MouseButton.RightButton:
                self.StartCreatingLink(mousePos)
                result = True
            #removing elements with MMB
            elif event.button() == Qt.MouseButton.MiddleButton:
                object = self.GetObjectUnderMouse(mousePos)
                if object:
                    self.RemoveObject(object)
                    result = True

        elif type == QEvent.MouseButtonRelease:
            #finishing link creation process (updating in link itself)
            #it is here because it needs to know on what node it finished
            if event.button() == Qt.MouseButton.RightButton:
                if self.currentLink:
                    self.EndCreatingLink(mousePos)
                    result = True
        
        if self.currentLink:
            result |= self.currentLink.ProcessInput(event)
        for link in self.objects:
            result |= link.ProcessInput(event)
        return result
        
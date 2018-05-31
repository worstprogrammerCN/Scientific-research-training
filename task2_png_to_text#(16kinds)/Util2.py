# -*- coding: utf-8 -*-
import json
import math
import queue

IMAGE_LENGTH = IMAGE_WIDTH = IMAGE_HEIGHT = 768

TYPES = ["unmovable", "tree", "movable"]
CATEGORIES_UNMOVABLE = ["bench", "bus", "car", "house"]
CATEGORIES_TREE = ["tree"]
CATEGORIES_MOVABLE = ["butterfly", "cat", "chicken", "cow", "dog", "duck", "people", "sheep", "bird", "pig", "rabbit"]

# 16 valid categories
INSTANCE = CATEGORIES_UNMOVABLE + CATEGORIES_TREE + CATEGORIES_MOVABLE + \
           ["cloud", "sun", "moon"] + \
           ["road", "grass"]

RANK = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",
        "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth",
        "nineteenth", "twentieth", "twenty-first", "twenty-second", "twenty-third", "twenty-fourth",
        "twenty-fifth", "twenty-sixth", "twenty-seventh", "twenty-eighth", "twenty-ninth", "thirtieth"]

NUMBER = [" ", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve",
          "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty",
          "Twenty-one", "Twenty-two", "Twenty-three", "Twenty-four", "Twenty-five", "Twenty-six",
          "Twenty-seven", "Twenty-eight", "Twenty-nine", "Thirty"]

RELATIVE_DIRECTIONS = ["left front", "front", "right front", "right", "left",
                       "left back", "back", "right back"]

DIRECTIONS = ["on the left front of", "in front of", "on the right front of", "on the right of" "on",
              "under", "one the left of", "on the left back of", "behind", "on the right back of"]


def get_type(category):
    if category in CATEGORIES_UNMOVABLE:
        return "unmovable"
    elif category in CATEGORIES_TREE:
        return "tree"
    elif category in CATEGORIES_MOVABLE:
        return "movable"
    else:
        return "other"


def get_opposite_relative_direction(relative_direction):
    """
    取得相反的方位。这个方位用于同类物体间相互区别时的定位。
    :param relative_direction: 自己所在的方位
    :return: 相反的方位
    """
    index = len(RELATIVE_DIRECTIONS) - 1 - RELATIVE_DIRECTIONS.index(relative_direction)
    return RELATIVE_DIRECTIONS[index]


def get_opposite_direction(direction):
    index = len(DIRECTIONS) - 1 - DIRECTIONS.index(direction)  # 自己所在的方向
    return DIRECTIONS[index]


class ItemOrGroupTypeError(TypeError):
    def __init__(self, o):
        TypeError.__init__(self, "item_or_group must be type of Item or ItemGroup. got %s" % type(o))


class Position(object):
    """是一个点。描述一个@code{Item}的位置。

    我们认为，每个@code{Item}都有自己的位置。
    位置有三个属性，离图片左侧的距离，离图片顶部的距离，还有层叠的顺序。

    Attributes:
        left: 点离图片左侧的距离。
        top: 点离图片顶部的距离。
        zIndex: 点在这张图片上的层叠顺序。1代表是第一个放置在图上的，2代表是在第一个Item放置后才放置在图上，以此类推。

    """

    def __init__(self, left, top, zIndex):
        super(Position, self).__init__()
        self.left = left
        self.top = top
        self.zIndex = zIndex

    def showPosition(self):
        print("position(left, top) is (%d,%d), zIndex is %d" % (self.left, self.top, self.zIndex))

    # 判断位置在另一个位置的左右、上下
    def is_above(self, position):
        return self.top < position.top

    def is_above_equal(self, position):
        return self.top <= position.top

    def is_below(self, position):
        return self.top > position.top

    def is_below_equal(self, position):
        return self.top >= position.top

    def is_left_of(self, position):
        return self.left < position.left

    def is_left_equal(self, position):
        return self.left <= position.left

    def is_right_of(self, position):
        return self.left > position.left

    def is_right_equal(self, position):
        return self.left >= position.left

    # 自己在另一个位置的右下
    def is_right_below_equal(self, position):
        return self.is_right_equal(position) and self.is_below_equal(position)

    # 自己在另一个位置的左上
    def is_left_above_equal(self, position):
        return self.is_left_equal(position) and self.is_above_equal(position)

    # 同水平/竖直线
    def is_vertical_to(self, position):
        return self.left == position.left

    def is_horizontal_to(self, position):
        return self.top == position.top

    # 判断两点重合
    def is_coincide_with(self, position):
        return self.left == position.left and self.top == position.top

    def get_degree_to(self, position):
        """得到与另一个位置的连线 与 水平线形成的角度

        Args:
            dx: 两个位置的水平距离，绝对值
            dy: 两个位置的竖直距离，绝对值
            degree: 两个

        Returns:
            一个角度。自己与另一个位置的连线 与 水平线形成的角度。
            这个角度可以是钝角或者锐角，我们取锐角的大小。
            当@code{dx}为0时, 角度为90度，直接返回90。
        """
        dx = abs(self.left - position.left)
        dy = abs(self.top - position.top)
        if dx == 0:
            return 90
        return math.atan(dy / dx) / math.pi * 180


class Size(object):
    """一个@code{Item}所占矩形区域的大小

    我们认为，一个@code{Item}在一张图上所占区域是一个矩形，这个矩形就会有长和宽两个属性。

    Attributes:
        width: 矩形的宽
        height: 矩形的长

    """

    def __init__(self, width, height):
        super(Size, self).__init__()
        self.width = width
        self.height = height

    def showSize(self):
        print("width is", self.width, "and height is", self.height)


class Item(object):
    """每个Item都有数量，位置和大小的属性，还有自己的类型和编号(@code{oid})"""

    def __init__(self, category, oid, position, size, id):
        """
        Args:
            category: 物体的类型。比如"tree", "car"
            oid: 物体的编号。比如"tree3", "cat2"
            position：物体的位置。
            size：物体的大小。
            id: 对应main中输入的class_id在list中的位置。
        """
        super(Item, self).__init__()
        self.category = category
        self.type = get_type(self.category)
        self.oid = oid
        self.position = position
        self.size = size
        self.id = id
        self.center: Position = Position(position.left + size.width / 2, position.top + size.height / 2,
                                         position.zIndex)
        self.bottom_center = Position(position.left, position.top + size.height / 2,
                                      position.zIndex)
        self.is_grouped = False
        self.num = 1
        self._name = None
        self._reference = None
        self.direction = None

    def showPosition(self):
        self.position.showPosition()

    def showSize(self):
        self.size.showSize();

    def showCenter(self):
        print("center(left, top) is (%d, %d)" % (self.center.left, self.center.top))

    def showSelf(self):
        """
            输出自己左上角的位置，以及自己的所占矩形区域的大小。
        """
        print("--------------an %s----------------" % self.category)
        print("rect size:")
        self.size.showSize()
        print("-------------------------------------")

    def get_degree_to(self, item):
        """
            返回自己的下中心与对方的下中心的连线 与 水平线 形成的角度。
            这个角度可以是钝角或者锐角，我们取的是锐角的大小。
        """
        return self.bottom_center.get_degree_to(item.bottom_center)

    def is_horizontal_to(self, item_or_group):
        if isinstance(item_or_group, Item):
            item: Item = item_or_group
            return self.get_degree_to(item) <= 30
        elif isinstance(item_or_group, ItemGroup):
            item_group: ItemGroup = item_or_group
            return item_or_group.top <= self.bottom <= item_group.bottom
        else:
            raise TypeError("item_or_group must be instance of Item or ItemGroup.")

    def is_vertical_to(self, item_or_group):
        if isinstance(item_or_group, Item):
            item: Item = item_or_group
            return self.get_degree_to(item) >= 60
        elif isinstance(item_or_group, ItemGroup):
            item_group: ItemGroup = item_or_group
            return self.is_center_within_both_sides(item_group)
        else:
            raise TypeError("item_or_group must be instance of Item or ItemGroup.")

    def is_bottom_edge_below(self, item_or_group):
        """
            判断自己的底边 是否 在@code{item}的底边 的下方
        """
        if isinstance(item_or_group, Item):
            item: Item = item_or_group
            return self.bottom > item.bottom
        elif isinstance(item_or_group, ItemGroup):
            item_group: ItemGroup = item_or_group
            return self.bottom > item_group.bottom
        else:
            raise TypeError("item_or_group must be instance of Item or ItemGroup.")

    def is_bottom_edge_above(self, item_or_group):
        """
            判断自己的底边 是否 在@code{item}的底边 的上方
        """
        return not self.is_bottom_edge_below(item_or_group)

    @property
    def left(self):
        return self.position.left

    @property
    def right(self):
        return self.position.left + self.size.width

    @property
    def top(self):
        return self.position.top

    @property
    def bottom(self):
        return self.position.top + self.size.height

    @property
    def width(self):
        return self.size.width

    @property
    def height(self):
        return self.size.height

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, reference):
        if not isinstance(reference, (Item, ItemGroup)):
            raise TypeError("reference must be type of Item or ItemGroup. got %s" % type(reference))
        self._reference = reference

    @property
    def be_verb(self):
        return "is"

    @property
    def image_position(self):
        room_length = IMAGE_LENGTH / 3
        image_positions = [["left back", "middle back", "right back"],
                           ["left", "middle", "right"],
                           ["left front", "middle", "right front"]]
        x = math.floor(self.bottom / room_length)
        y = math.floor(self.center.left / room_length)
        return "%s of the image" % image_positions[x][y]

    def is_near(self, item):
        return self.edge_distance(item) <= 100

    # 以下5个函数都是比较自己的中心与对方的位置的
    def is_center_right_of(self, item_or_group):
        if isinstance(item_or_group, Item) or isinstance(item_or_group, ItemGroup):
            return self.center.is_right_of(item_or_group.center)
        else:
            raise TypeError("item_or_group must be instance of Item or ItemGroup.")

    def is_center_left_of(self, item_or_group):
        if isinstance(item_or_group, Item) or isinstance(item_or_group, ItemGroup):
            return not self.is_center_right_of(item_or_group)
        else:
            raise TypeError("item_or_group must be instance of Item or ItemGroup.")

    def is_center_above(self, item_or_group):
        if isinstance(item_or_group, Item) or isinstance(item_or_group, ItemGroup):
            return self.center.is_above(item_or_group.center)
        else:
            raise TypeError("item_or_group must be instance of Item or ItemGroup.")

    def is_center_below(self, item_or_group):
        if isinstance(item_or_group, Item) or isinstance(item_or_group, ItemGroup):
            return not self.center.is_above(item_or_group.center)
        else:
            raise TypeError("item_or_group must be instance of Item or ItemGroup.")

    def is_center_within_both_sides(self, item_or_group):
        if isinstance(item_or_group, (Item, ItemGroup)):
            return item_or_group.left <= self.center.left <= item_or_group.right
        else:
            raise ItemOrGroupTypeError(item_or_group)

    def edge_distance(self, item_or_group):
        """返回两个对象的"边距离"

        "边距离"是临时构造的词语，通过计算两个对象最接近的两条边的距离，
        来形象地反映两个物体间的远近程度。
        比如@code{self}在左下，@code{item}在右上，
        那么@code{dy}是@code{self}的顶边与@code{item}的底边的竖直距离
        @code{dx}是@code{self}的右边与@code{item}的左边的水平距离
        然后我们取距离为@code{sqrt(dx ^ 2 + dy ^ 2)}

        Args:
            dy: @code{self}与@code{item}的最近的顶/底边之间的竖直距离。这个值必须为非负数
            dx: @code{self}与@code{item}的最近的左/右边之间的水平距离。这个值必须为非负数
            item_or_group: 类型是Item或ItemGroup。计算自己到该对象的边距离
        Returns:
            两个对象最接近的两条边的距离。
        """
        if not isinstance(item_or_group, (Item, ItemGroup)):
            raise ItemOrGroupTypeError(item_or_group)
        dy = 0
        if self.top > item_or_group.bottom:
            dy = abs(self.top - item_or_group.bottom)
        elif self.bottom < item_or_group.top:
            dy = abs(self.bottom - item_or_group.top)

        dx = 0
        if self.left > item_or_group.right:
            dx = abs(self.left - item_or_group.right)
        elif self.right < item_or_group.left:
            dx = abs(self.right - item_or_group.left)

        return math.sqrt(dx ** 2 + dy ** 2)

    def get_single_noun(self):
        if self.category == "people":
            return "person"
        return self.category

    def get_noun(self):
        return self.get_single_noun()

    def get_noun_with_num(self, is_sentence_head=False):
        if is_sentence_head:
            return "A %s" % self.get_single_noun()
        else:
            return "a %s" % self.get_single_noun()

    def get_position_to_item(self, item=None):
        """
        得到关于item的方位。用于同种类别物体的比较。
        :param item:
        :return: 关于item的方位
        """
        degree = self.get_degree_to(item)
        if self.is_bottom_edge_above(item):  # 在item后方
            if degree > 65:
                return "back"
            elif 30 <= degree <= 65:
                if self.is_center_right_of(item):
                    return "right back"
                else:
                    return "left back"
        elif self.is_bottom_edge_below(item):
            if degree > 65:
                return "front"
            elif 30 <= degree <= 65:
                if self.is_center_right_of(item):
                    return "right front"
                else:
                    return "left front"
        if self.is_center_right_of(item):
            return "right"
        elif self.is_center_left_of(item):
            return "left"

    def get_position_to_item_group(self, item_group=None):
        """
        得到关于item_group的方位。用于同种类别物体的比较。
        :param item_group:
        :return:
        """
        if self.is_vertical_to(item_group):
            if self.is_bottom_edge_above(item_group):
                return "back"
            else:
                return "front"
        elif self.is_horizontal_to(item_group):
            if self.is_center_right_of(item_group):
                return "right"
            else:
                return "left"
        elif self.is_center_right_of(item_group):
            if self.is_bottom_edge_above(item_group):
                return "right back"
            else:
                return "right front"
        elif self.is_center_left_of(item_group):
            if self.is_bottom_edge_above(item_group):
                return "left back"
            else:
                return "left front"

    def get_position_to(self, reference):
        """
        item --position--> self
        得到关于reference的方位。用于对[同种类别却不属于同一group的物体]进行方位比较。
        :param reference: 可选参数。表示与自己进行方位对比的Item或ItemGroup
        :return: 自己与另一个Item或ItemGroup对比所在的方位。
        """
        if isinstance(reference, Item):
            return self.get_position_to_item(reference)
        elif isinstance(reference, ItemGroup):
            return self.get_position_to_item_group(reference)
        else:
            raise TypeError("reference must be instance of Item or ItemGroup")

    def get_name(self, is_sentence_head=False):
        if not is_sentence_head:
            return self._name
        else:
            return "The" + self._name[3:]

    def set_name(self, num_total, reference=None, index=None, opposite_direction=None):
        """

        提供参数的方式：(num_total, reference) (num_total, index) (num_total, opposite_direction)
        :param num_total:
        :param reference:
        :param index:
        :param opposite_direction: 可选参数。提供opposite_direction，说明自己这类Item有两个，
        且另一个Item或ItemGroup处于二者中的 opposite_direction方位，
        自己处在二者中的direction(left, right, left front等)方位。
        :return:
        """
        if num_total < 1:
            raise ValueError("num_total must be greater than 1.")

        if opposite_direction is not None:  # 有两个此类物体，且参数提供了另一个物体所在方位
            direction = get_opposite_relative_direction(opposite_direction)  # 自己所在的方向
            self._name = "the %s %s" % (direction, self.get_single_noun())
            return None

        if num_total == 1:
            self._name = "the %s" % self.get_single_noun()
            return None
        elif num_total == 2:
            direction = self.get_position_to(reference)
            self._name = "the %s %s" % (direction, self.get_single_noun())
            return direction
        else:
            self._name = "the %d left %s" % (RANK[index], self.get_single_noun())
            return None


class ItemGroup(object):
    def __init__(self, items: [Item]):
        if not isinstance(items, type([Item])):
            raise TypeError("type of items must be [Item]")
        if len(items) == 0:
            raise ValueError("length of items must be longer than 0.")
        self.items = items
        self.category = items[0].category
        self.type = get_type(self.category)
        self._avg_item = self.get_avg_item(items)

        # 找到这一组Item的最左和最右、最上、最下的位置。
        self.right = max([item.right for item in items])
        self.left = min([item.left for item in items])
        self.top = min([item.bottom for item in items])  # 取落脚点最高的位置
        self.bottom = max([item.bottom for item in items])  # 取落脚点最低的位置
        self.bottom_center = Position((self.left + self.right) / 2, self.bottom, 0)

        self._name = None
        self._reference = None
        self.direction = None

    @staticmethod
    def get_avg_item(items):
        """
            输入一个同类型的item数组，计算它们的平均位置和大小，合并成一个item并返回
        """
        category = items[0].category
        oid = items[0].oid
        total_left = 0
        total_top = 0
        z_index = items[0].position.zIndex

        total_height = 0
        total_width = 0
        num = 0

        for item in items:
            total_left += item.position.left
            total_top += item.position.top
            total_height += item.size.height
            total_width += item.size.width
            num += 1

        position = Position(total_left / num, total_top / num, z_index)
        size = Size(total_width / num, total_height / num)
        id = -1

        item = Item(category, oid, position, size, id)
        item.num = num
        return item

    @property
    def num(self):
        return len(self.items)

    @property
    def center(self):
        return self._avg_item.center

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, reference):
        if not isinstance(reference, (Item, ItemGroup)):
            raise TypeError("reference must be type of Item or ItemGroup. got %s" % type(reference))
        self._reference = reference

    @property
    def be_verb(self):
        return "are"

    @property
    def noun(self):
        return self.get_plural_noun()

    @property
    def image_position(self):
        return "back"

    def get_noun_with_num(self, is_sentence_head=False):
        return "%d %s" % (self.num, self.get_plural_noun())

    def is_center_right_of(self, item_or_group):
        if isinstance(item_or_group, Item) or isinstance(item_or_group, ItemGroup):
            return self.center.is_right_of(item_or_group.center)
        else:
            raise TypeError("item_or_group must be instance of Item or ItemGroup.")

    def is_center_left_of(self, item_or_group):
        if isinstance(item_or_group, Item) or isinstance(item_or_group, ItemGroup):
            return not item_or_group.is_center_right_of(self)
        else:
            raise TypeError("item_or_group must be instance of Item or ItemGroup.")

    def is_center_above(self, item_or_group):
        if isinstance(item_or_group, Item) or isinstance(item_or_group, ItemGroup):
            return self.center.is_above(item_or_group.center)
        else:
            raise TypeError("item_or_group must be instance of Item or ItemGroup.")

    def is_center_within_both_sides(self, item_or_group):
        if isinstance(item_or_group, (Item, ItemGroup)):
            return item_or_group.left <= self.center.left <= item_or_group.right
        else:
            raise ItemOrGroupTypeError(item_or_group)

    def is_foot_inside(self, item_group):
        if not isinstance(item_group, ItemGroup):
            raise TypeError("item_group must be of type ItemGroup. got %s" % type(item_group))
        return item_group.top <= self.bottom <= item_group.bottom and \
               self.is_center_within_both_sides(item_group)

    def get_degree_to(self, item_or_group):
        """
            返回自己的中心与对方的中心的连线 与 水平线 形成的角度。
            这个角度可以是钝角或者锐角，我们取的是锐角的大小。
        """
        return self.center.get_degree_to(item_or_group.center)

    def is_vertical_to(self, item_or_group):
        if isinstance(item_or_group, Item):
            item: Item = item_or_group
            return self.get_degree_to(item) >= 60
        elif isinstance(item_or_group, ItemGroup):
            item_group: ItemGroup = item_or_group
            border_range = 20
            return self.right >= item_group.left - border_range and self.left <= item_group.right + border_range
        else:
            raise TypeError("item_or_group must be instance of Item or ItemGroup.")

    def is_horizontal_to(self, item_or_group):
        if isinstance(item_or_group, Item):
            item: Item = item_or_group
            return self.get_degree_to(item) <= 30
        elif isinstance(item_or_group, ItemGroup):
            item_group: ItemGroup = item_or_group
            return item_or_group.top <= self.center.top <= item_group.bottom
        else:
            raise TypeError("item_or_group must be instance of Item or ItemGroup.")

    def get_plural_noun(self):
        if self.category in ["people", "sheep"]:
            return self.category
        if self.category[-1] == "y":
            return self.category[:-1] + "ies"
        elif self.category[-1] == "s" or self.category[-2:] == "ch":
            return self.category + "es"
        else:
            return self.category + "s"

    def get_noun(self):
        return self.get_plural_noun()

    def get_position_to_item_group(self, item_group):
        """
        :param item_group: 另一群同类群体
        :return: 对于另一群同类物体的方位
        """
        if self.is_vertical_to(item_group):
            if self.is_center_above(item_group):
                return "back"
            else:
                return "front"
        if self.is_center_right_of(item_group):
            return "right"
        else:
            return "left"

    def get_position_to(self, item_or_group):
        if isinstance(item_or_group, Item):
            opposite_direction = item_or_group.get_position_to(self)
            return get_opposite_relative_direction(opposite_direction)
        elif isinstance(item_or_group, ItemGroup):
            return self.get_position_to_item_group(item_or_group)
        else:
            raise TypeError("item_or_group must be type of Item or ItemGroup.")

    def edge_distance(self, item_or_group):
        if not isinstance(item_or_group, (Item, ItemGroup)):
            raise ItemOrGroupTypeError(item_or_group)
        dy = 0
        if self.top > item_or_group.bottom:
            dy = abs(self.top - item_or_group.bottom)
        elif self.bottom < item_or_group.top:
            dy = abs(self.bottom - item_or_group.top)

        dx = 0
        if self.left > item_or_group.right:
            dx = abs(self.left - item_or_group.right)
        elif self.right < item_or_group.left:
            dx = abs(self.right - item_or_group.left)

        return math.sqrt(dx ** 2 + dy ** 2)

    def get_name(self, is_sentence_head=False):
        if not is_sentence_head:
            return self._name
        else:
            return "The" + self._name[3:]

    def set_name(self, num_total, reference=None, index=None, opposite_direction=None):
        """

        :param num_total: 这类的物体的总数
        :param reference: 要进行方位比较的物体对象
        :param index: 自己在这类物体中从后到前的次序
        :param opposite_direction: 另一个物体相对自己的方位
        :return:
        """
        if num_total < 1:
            raise ValueError("num_total must be greater than 1.")

        if opposite_direction is not None:  # 有两个此类物体，且参数提供了另一个物体所在方位
            direction = get_opposite_relative_direction(opposite_direction)
            self._name = "the %s %s" % (direction, self.get_plural_noun())
            return None

        if num_total == 1:
            self._name = "the %s" % self.get_plural_noun()
            return None
        elif num_total == 2:
            direction = self.get_position_to(reference)
            self._name = "the %s %s" % (direction, self.get_plural_noun())
            return direction
        else:
            self._name = "the %d left %s" % (RANK[index], self.get_plural_noun())
            return None

    def find_reference(self, unmovable_reference=None, tree_reference=None, used_reference=None):
        if used_reference is None:
            # 描述本group时，并没有使用过参照物，说明这个group是图片中最靠后的(在collection定是第一个group)，且没有更高优先级的物体了，
            # 所以根本就找不到参照物。
            # group内第一个item不用找参照物，后面的每个item都以前面的为参照物
            for index, item in enumerate(self.items[1:]):
                former_item: Item = self.items[index - 1]
                item: Item.reference = former_item
                item.direction = ItemCollection.get_dir_of_item(former_item, item)

        """
        为group内第一个Item找参照物
       """
        first_item: Item = self.items[0]
        if self.type == "unmovable" or self.type == "tree":
            if len(unmovable_reference) == 1:
                # 只有一个可参照物，这个必定是使用过的那个。
                # 但没有别的参照物能用了，首个item只能依然用这个
                nearest: Item = unmovable_reference[0]
            else:
                # 有充足的参照物时，选择未使用过的最近的参照物
                unmovable_reference.remove(used_reference)
                nearest: Item = min(unmovable_reference, key=lambda x: x.edge_distance(first_item))
        if self.type == "movable":
            # 预设条件: 静物至少有一个，树/树群可能有也可能没有
            if len(unmovable_reference) == 1 and len(tree_reference) > 0:
                nearest: Item = tree_reference[0]
            elif len(unmovable_reference) == 1 and len(tree_reference) == 0:
                nearest: Item = unmovable_reference[0]
            elif len(unmovable_reference) > 1:
                # 有充足的参照物时，选择未使用过的最近的参照物
                unmovable_reference.remove(used_reference)
                nearest: Item = min(unmovable_reference, key=lambda x: x.edge_distance(first_item))
        first_item.direction = ItemCollection.get_dir_of_item(nearest, first_item)
        first_item.reference = nearest

        """
        从第二个开始的每个Item都以前面的item为参照
       """
        for index, cur_item in enumerate(self.items[1:]):
            reference = self.items[index - 1]
            cur_item.direction = ItemCollection.get_dir_of_item(reference, cur_item)
            cur_item.reference = reference


class ItemCollection(object):
    MODES = ["unmovable", "tree", "movable"]

    def __init__(self, dict_collection, unmovable_reference=None, tree_reference=None):
        """

        :param dict_collection: 自己包含的物体集合。可以是静物、树或者动物。
        :param unmovable_reference: 可作为参照物的静物们
        :param tree_reference: 可作为参照物的树/树群们

        self.collection: 元素是Item或ItemGroup, 元素间的顺序从后往前排列,
        但单个group内各元素的顺序不一定按照顺序排列。
        """
        if not isinstance(dict_collection, type({str: []})):
            raise TypeError("type of dict_collection must be {str: []}.", type(dict_collection))

        self.index = []

        # 为dict_collection每个item或group设置称呼
        self.num_total = {}
        for category in dict_collection:
            items_group = dict_collection[category]
            ItemCollection._set_name_for_item_or_groups(items_group)
            num_total = 0
            for item in items_group:
                num_total += item.num
            self.num_total[category] = num_total

        self.collection: [] = ItemCollection.compress_dict(dict_collection)

        if unmovable_reference is None and tree_reference is None:
            self.mode = "unmovable"
            self.find_reference()
        elif tree_reference is None:
            self.mode = "tree"
            self.unmovable: [] = ItemCollection.compress_dict(unmovable_reference)
            self.find_reference(self.unmovable)
        else:
            self.mode = "movable"
            self.unmovable: [] = ItemCollection.compress_dict(unmovable_reference)
            self.trees: [] = ItemCollection.compress_dict(tree_reference)
            self.find_reference(self.unmovable, self.trees)

    def find_reference(self, unmovable_reference=None, tree_reference=None):
        """
        为collection里的每个Item或ItemGroup找到参照物。
        参照物只能在top比自己小(在自己后面)的物体里找，自己后面没有能作参照物的物体。
        如果collection都是静物，则参照物只在静物里找。如果是第一个物体，则不需要找参照物。
        如果collection都是树，则参照物也只在静物里找。如果没有静物，则第一个树/树群不需要找参照物。
        如果collection都是动物，则参照物先在静物里找，若没有静物，则在动物里找。
        :param tree_reference:
        :param unmovable_reference:
        :return:
        """
        if self.mode == "unmovable":
            # 静物以静物为参照物
            # 第一个静物不需要找参照物，描述方位时只需要描述"in the middle", "in the right"等等
            # 后面的每个参照物都以描述过的物体中最近的作为参照物
            for index, cur_item in enumerate(self.collection):
                reference_candidate = self.collection[:index]
                if index != 0:  # 第一个unmovable物体不用找参照物
                    nearest = min(reference_candidate, key=lambda x: cur_item.edge_distance(x))
                    cur_item.direction = ItemCollection.get_dir_of(nearest, cur_item)
                    cur_item.reference = nearest
                else:
                    nearest = None

                if isinstance(cur_item, ItemGroup):
                    cur_item.find_reference(unmovable_reference=reference_candidate,
                                            used_reference=nearest)
        elif self.mode == "tree":
            if len(unmovable_reference) == 0:
                for index, cur_item in enumerate(self.collection):
                    reference_candidate = self.collection[:index]
                    if index != 0:
                        # 没有静物时，第一个树/树群不需要找参照物。只需要描述方位，比如"in the middle"即可。
                        # 第一个树/树群后的每棵树都以前面的树/树群作为参照物
                        nearest = min(reference_candidate, key=lambda x: cur_item.edge_distance(x))
                        cur_item.direction = ItemCollection.get_dir_of(nearest, cur_item)
                        cur_item.reference = nearest
                    else:
                        nearest = None

                    if isinstance(cur_item, ItemGroup):
                        cur_item.find_reference(tree_reference=reference_candidate,
                                                used_reference=nearest)
            else:
                # 有静物时，所有树/树群都以静物作为参照物
                reference_candidate = unmovable_reference
                for index, cur_item in enumerate(self.collection):
                    nearest = min(reference_candidate, key=lambda x: cur_item.edge_distance(x))
                    cur_item.direction = ItemCollection.get_dir_of(nearest, cur_item)
                    cur_item.reference = nearest

                    if isinstance(cur_item, ItemGroup):
                        cur_item.find_reference(unmovable_reference=unmovable_reference,
                                                tree_reference=self.collection[:index],
                                                used_reference=nearest)
        elif self.mode == "movable":
            # 有静物就以静物作为参照物
            # 无静物就以树作为参照物。
            # 代码默认不会出现既没有静物又没有树的情况
            if len(unmovable_reference) > 0:
                reference_candidate = unmovable_reference
            else:
                reference_candidate = tree_reference

            for index, cur_item in enumerate(self.collection):
                nearest = min(reference_candidate, key=lambda x: cur_item.edge_distance(x))
                cur_item.direction = ItemCollection.get_dir_of_item(nearest, cur_item)
                cur_item.reference = nearest

                if isinstance(cur_item, ItemGroup):
                    cur_item.find_reference(unmovable_reference=unmovable_reference,
                                            tree_reference=tree_reference,
                                            used_reference=nearest)
        else:
            raise ValueError("mode must be one of the %s. got %s" % (self.MODES, self.mode))

    @staticmethod
    def get_dir_of_item(this, that: Item):
        """
            :param that: 类别为Item
            this->direc->that
            如果that在this的左边，则返回on the left of，即[that] is [one the left of] [this].
        """
        insect = ["butterfly"]
        if that.is_vertical_to(this):
            if that.is_bottom_edge_above(this):
                return "behind"
            else:
                return "in front of"
        elif that.is_horizontal_to(this):
            if that.is_center_right_of(this):
                return "on the right of"
            else:
                return "on the left of"
        elif that.is_center_right_of(this):
            if that.is_bottom_edge_above(this):
                return "on the right back of"
            else:
                return "on the right front of"
        elif that.is_center_left_of(this):
            if that.is_bottom_edge_above(this):
                return "on the left back of"
            else:
                return "on the left front of"

    @staticmethod
    def get_dir_of_item_group(this, that: ItemGroup):
        """
        :param this: 类别为Item或ItemGroup
        :param that: 类别为Item
        :return: that
        """
        if isinstance(this, Item):
            opposite_direction = ItemCollection.get_dir_of_item(that, this)
            return get_opposite_direction(opposite_direction)
        elif not isinstance(this, ItemGroup):
            raise TypeError("this must be of type Item or ItemGroup. got %s" % type(this))

        if that.is_foot_inside(this):
            return "among"

        if that.is_vertical_to(this):
            if that.is_center_above(this):
                return "behind"
            else:
                return "in front of"
        if that.is_center_right_of(this):
            return "on the right of"
        else:
            return "on the left of"

    @staticmethod
    def get_dir_of(this, that):
        if isinstance(that, Item):
            return ItemCollection.get_dir_of_item(this, that)
        elif isinstance(that, ItemGroup):
            return ItemCollection.get_dir_of_item_group(this, that)
        else:
            raise ItemOrGroupTypeError(that)

    @staticmethod
    def compress_dict(dict_collection: {str: []}):
        compressed = []
        for collection in dict_collection.values():
            for item_or_group in collection:
                compressed.append(item_or_group)
        return sorted(compressed, key=lambda x: x.bottom)

    @staticmethod
    def get_collections(ground_items, categories_unmovable, categories_movable):
        unmovable: {str: []} = ItemCollection._get_collection(ground_items, categories_unmovable)
        trees: {str: []} = ItemCollection._get_collection(ground_items, ["tree"])
        movable: {str: []} = ItemCollection._get_collection(ground_items, categories_movable)

        return ItemCollection(unmovable), ItemCollection(trees, unmovable), ItemCollection(movable, unmovable, trees)

    @staticmethod
    def _get_collection(ground_items, categories):
        items = [item for item in ground_items if item.category in categories]
        collection: {str: []} = ItemCollection._merge_same_item(items)
        return collection

    @staticmethod
    def _merge_same_item(items: [Item]):
        if len(items) == 0:
            print("items length should be longer than 0.")
            return
        items_set = set(items)
        process_queue = queue.Queue()
        items_groups = {}

        while len(items_set) > 0:
            # let the first item be processed.
            first_item_in_group: Item = items_set.pop()
            process_queue.put(first_item_in_group)
            group_category = first_item_in_group.category
            items_group = [first_item_in_group]

            while not process_queue.empty():
                cur_item: Item = process_queue.get()
                for item in items_set:
                    if item.category == group_category and item.is_near(
                            cur_item) and not item.is_grouped:  # item is in the same group
                        process_queue.put(item)
                        items_group.append(item)
                        item.is_grouped = True
                    items_set = items_set.difference(items_group)  # 已经加入组的item不用再处理

            if not items_groups.get(group_category):
                items_groups[group_category] = []
            if len(items_group) > 1:
                items_groups[group_category].append(ItemGroup(items_group))
            else:
                items_groups[group_category].append(items_group[0])
        return items_groups

    @staticmethod
    def _set_name_for_item_or_groups(item_or_groups: []):
        """
        接收一个参数，为items里的每个item设置称呼
        :param item_or_groups: list。元素类型为Item或ItemGroup
        :return:
        """
        num_total = len(item_or_groups)
        for item in item_or_groups:
            if not isinstance(item, (Item, ItemGroup)):
                raise TypeError("type of each entry in items must be Item or ItemGroup")
        if num_total == 1:  # only one
            item_or_groups[0].set_name(num_total=1)
        elif num_total == 2:  # only two
            first = item_or_groups[0]
            second = item_or_groups[1]
            direction = first.set_name(num_total=2, reference=second)
            second.set_name(num_total=2, opposite_direction=direction)
        else:
            item_or_groups = sorted(item_or_groups, key=lambda x: x.position.left)
            for item_or_group, index in item_or_groups:
                item_or_group.set_name(num_total=num_total, index=index)

    @staticmethod
    def get_single_noun(category):
        if category == "people":
            return "person"
        return category

    @staticmethod
    def get_plural_noun(category):
        if category in ["people", "sheep"]:
            return category
        if category[-1] == "y":
            return category[:-1] + "ies"
        elif category[-1] == "s" or category[-2:] == "ch":
            return category + "es"
        else:
            return category + "s"

    @staticmethod
    def get_noun(category, num):
        if num == 1:
            return ItemCollection.get_single_noun(category)
        elif num > 1:
            return ItemCollection.get_plural_noun(category)
        else:
            raise ValueError("num must be larger than 0. got %d" % num)

    def get_description(self):
        indexes = []
        each_description = []

        for item_or_group in self.collection:
            item_name = item_or_group.get_name(is_sentence_head=True)
            be_verb = item_or_group.be_verb

            if item_or_group.reference is not None:
                # 有参照物
                noun_with_num = item_or_group.get_noun_with_num(is_sentence_head=True)
                description = "%s %s %s %s." % (noun_with_num, be_verb,
                                                item_or_group.direction, item_or_group.reference.get_name())
            else:
                # 无参照物，直接描述方位
                image_position = item_or_group.image_position
                description = "%s %s on the %s." % (item_name, be_verb, image_position)

            if isinstance(item_or_group, Item):
                indexes.append(item_or_group.id)

            if isinstance(item_or_group, ItemGroup) and item_or_group.category != "tree":
                # 对于group内每个Item还要描述

                for index, item in enumerate(item_or_group.items):
                    item: Item
                    item_index = item.id
                    item_noun: str = item.get_noun()
                    direction: str = item.direction

                    indexes.append(item_index)
                    if index == 0:
                        reference_name = item.reference.get_name()
                        description += " The first %s is %s %s." % (item_noun, direction, reference_name)
                    else:
                        reference_noun = item.reference.get_noun()
                        # print(item_noun, reference, item.bottom, item.reference.bottom, direction)
                        description += " The %s %s is %s the %s %s." % (RANK[index], item_noun,
                                                                        direction, RANK[index - 1], reference_noun)
            elif item_or_group.category == "tree":
                indexes.extend([item.id for item in item_or_group.items])

            each_description.append(description)

        description = []
        description.extend(each_description)
        return " ".join(description), indexes


def init_dict_item(dict_item):
    """
    初始化物体的字典。
        读取处理'./colorMap_46.txt'得到物体与编号对应关系的dict。
        Args:
            dict_item: 字典。key是整形数，含义是编号；value是字符串，含义是物体的名字
    :return: 物体与编号对应关系的dict
    """

    f = open('./colorMap_46.txt')

    index = 0
    for line in f.readlines():
        index += 1
        item = line.split(" ")[0]
        dict_item[index] = item


dict_item = {}
init_dict_item(dict_item)


def read(pred_boxes, pred_class_ids):
    items = []
    for i in range(0, len(pred_class_ids)):
        category = dict_item[pred_class_ids[i]]
        if category in INSTANCE:  # the category is valid
            left = pred_boxes[i][1]
            top = pred_boxes[i][0]
            width = pred_boxes[i][3] - pred_boxes[i][1]
            height = pred_boxes[i][2] - pred_boxes[i][0]
            id = i
            oid = "%s%d" % (category, i)
            position = Position(left, top, oid)
            size = Size(width, height)
            item = Item(category, oid, position, size, id)
            items.append(item)
    return items

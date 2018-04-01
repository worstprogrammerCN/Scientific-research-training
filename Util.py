import argparse
import json
import math


parser = argparse.ArgumentParser()
parser.add_argument("--json_dir", type=str, default="results1_test/results1/", help="Json Directory")
args = parser.parse_args()


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
		print("position(left, top) is (%d,%d), zIndex is %d" % (self.left, self.top, self.zIndex) )

	# 判断位置在另一个位置的前后、左右、上下
	def isFrontOf(self, position):
		return self.zIndex > position.zIndex
	def isBehindOf(self, position):
		return self.zIndex < position.zIndex

	def isAbove(self, position):
		return self.top < position.top
	def isAboveEqual(self, position):
		return self.top <= position.top
	def isBelow(self, position):
		return self.top > position.top
	def isBelowEqual(self, position):
		return self.top >= position.top

	def isLeftOf(self, position):
		return self.left < position.left
	def isLeftEqual(self, position):
		return self.left <= position.left
	def isRightOf(self, position):
		return self.left > position.left
	def isRightEqual(self, position):
		return self.left >= position.left

	# 位置在另一个位置的右下或左上
	def isRightBelowEqual(self, position):
		return self.isRightEqual(position) and self.isBelowEqual(position)
	def isLeftAboveEqual(self, position):
		return self.isLeftEqual(position) and self.isAboveEqual(position)

	# 同水平/竖直线	
	def isVerticalTo():
		return self.left == position.left
	def isHorizontalTo():
		return self.top == position.top

	# 判断两点重合
	def isCoincideWith(self, position):
		return self.left == position.left and self.top == position.top

	# 判断点是否在物体所占矩形区域内。
	def isInside(self, item):
		return self.isRightBelowEqual(item.leftTop) and self.isLeftAboveEqual(item.rightBottom)

	def getDegreeTo(self, position):
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
	"""每个Item都有位置和大小的属性，还有自己的类型和编号(@code{oid})"""
	def __init__(self, category, oid, position, size):
		"""
		Args:
			category: 物体的类型。比如"tree", "car"
			oid: 物体的编号。比如"tree3", "cat2"
			position：物体的位置。
			size：物体的大小
			leftTop：一个@code{position}，物体所占矩形的左上角
			rightBottom: 一个code{position}, 物体所占矩形的右下角

			dir: 
				字典。仅第一级的物体才用到的属性。
				一级物体通过这个属性可以定位关联到自己上的二级物体，并产生它们的描述。
				@code{key}是各种位置的描述，比如"in front of", "on the right of"等等。
				@code{value}是数组，包含这个位置关系上的第二级@code{item}。
				比如，如果自己的右边有两个其他@code{item}，则有{"on the right of" : ['Item', 'Item']}
			nextItem:
				@code{item}。仅第一级的物体才用到的属性。
				表示与自己最近的第一级的物体。
				通过这个属性可以定位下一个最近的一级物体。
			nextDir:
				字符串。仅第一级的物体才用到的属性。
				表示与自己最近的第一级的物体与自己的位置关系。
				比如"in front of", "on the right of"等等。
		"""
		super(Item, self).__init__()
		self.category = category
		self.oid = oid
		self.position = position
		self.size = size
		self.center = Position(position.left + size.width / 2, position.top + size.height / 2, position.zIndex)
		self.leftTop = self.position
		self.rightBottom = Position(position.left + size.width, position.top + size.height, position.zIndex)

		self.dir = {}
		self.nextItem = None
		self.nextDir = ""

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
		print("leftTop:")
		self.leftTop.showPosition()
		print("rect size:")
		self.size.showSize()
		print("-------------------------------------")

	def isInteractWith(self, item):
		"""
			判断两个item是否相交。关键在于判断它们占有的矩形区域是否相交。
			详细的判断逻辑较难阐述，百度上有很多解释清楚的，此处省去逻辑。
		"""
		if self.leftTop.isRightOf(item.rightBottom) or self.leftTop.isBelow(item.rightBottom):
			return False
		if self.leftTop.isInside(item):
			return True
		elif self.rightBottom.isInside(item):
			return True
		elif self.leftTop.isLeftOf(item.leftTop) and self.rightBottom.isRightBelowEqual(item.leftTop): # 从左向右跨越覆盖
			return True
		elif self.leftTop.isAbove(item.leftTop) and self.rightBottom.isBelowEqual(item.leftTop): # 从上到下跨越覆盖
			return True 
		return False
	
	def getDegreeTo(self, item):
		"""
			返回自己的中心与对方的中心的连线 与 水平线 形成的角度。
			这个角度可以是钝角或者锐角，我们取的是锐角的大小。
		"""
		return self.center.getDegreeTo(item.center)

	def isHorizonTalTo(self, item):
		return self.getDegreeTo(item) <= 30

	def isVerticalTo(self, item):
		return self.getDegreeTo(item) >= 60

	def isDiagonalTo(self, item):
		degree = self.getDegreeTo(item)
		return degree > 30 and degree < 60

	def isBottomEdgeBelow(self, item):
		"""
			判断自己的底边 是否 在@code{item}的底边 的下方
		"""
		return self.position.top + self.size.height > item.position.top + item.size.height

	def isBottomEdgeAbove(self, item):
		"""
			判断自己的底边 是否 在@code{item}的底边 的上方
		"""
		return self.position.top + self.size.height <= item.position.top + item.size.height

	"""
	以下8个函数，包含了判断自己与@code{item}的位置关系。
	位置关系有8种：
		在对方上方，前方，左边，右边。
		以及左前，右前，左后，右后。
	注意:
		由于给定的信息有限，我们难以在平面图上分辨两个物体间的关系是"on"还是"behind"。此处一概认为是"on"
	"""

	# 判断是否在@code{item}的正右侧
	# 比较中心是否基本水平，且自己的@code{center}在对方的@code{center}的右侧
	def isRightOf(self, item):
		return self.isHorizonTalTo(item) and self.center.isRightOf(item.center)

	# 判断是否在@code{item}的正左侧
	# 原理同上。
	def isLeftOf(self, item):
		return self.isHorizonTalTo(item) and self.center.isLeftOf(item.center)

	# 判断是否在@code{item}的正前方
	# 首先，自己的底边要在对方的底边之下，其次，要基本竖直对齐
	def isFrontOf(self, item):
		return (self.isBottomEdgeBelow(item) or self.center.isFrontOf(item.center) and self.isInteractWith(item)) and self.isVerticalTo(item)

	def isRightFrontOf(self, item):
		return self.isBottomEdgeBelow(item)\
		 and self.center.isRightOf(item.center)\
		 and self.isDiagonalTo(item)

	def isLeftFrontOf(self, item):
		return self.isBottomEdgeBelow(item)\
		 and self.center.isLeftOf(item.center)\
		 and self.isDiagonalTo(item)

	def isRightBehind(self, item):
		return self.isBottomEdgeAbove(item)\
		 and self.center.isRightOf(item.center)\
		 and self.isDiagonalTo(item)

	def isLeftBehind(self, item):
		return self.isBottomEdgeAbove(item)\
		 and self.center.isLeftOf(item.center)\
		 and self.isDiagonalTo(item)

	def isOn(self, item):
		return self.isBottomEdgeAbove(item)\
		 and self.isVerticalTo(item)

	def edgeDistance(self, item):
		"""返回两个对象的"边距离"
		
		"边距离"是临时构造的词语，用于形象地反映我想表示距离的方式。
		我们计算两个对象最接近的两条边的距离。
		比如@code{self}在左下，@code{item}在右上，
		那么@code{dy}是@code{self}的顶边与@code{item}的底边的竖直距离
		@code{dx}是@code{self}的右边与@code{item}的左边的水平距离
		然后我们取距离为@code{sqrt(dx ^ 2 + dy ^ 2)}

		Args:
			dy: @code{self}与@code{item}的最近的顶/底边之间的竖直距离。这个值必须为非负数
			dx: @code{self}与@code{item}的最近的左/右边之间的水平距离。这个值必须为非负数

		Returns:
			两个对象最接近的两条边的距离。
		"""
		dy = 0
		if self.leftTop.top > item.rightBottom.top:
			dy = abs(self.leftTop.top - item.rightBottom.top)
		elif self.rightBottom.top < item.leftTop.top:
			dy = abs(self.rightBottom.top - item.leftTop.top)
		
		dx = 0
		if self.leftTop.left > item.rightBottom.left:
			dx = abs(self.leftTop.left - item.rightBottom.left)
		elif self.rightBottom.left < item.leftTop.left:
			dx = abs(self.rightBottom.left - item.leftTop.left)

		return math.sqrt(dx ** 2 + dy ** 2)

	def findNearestItem(self, items, filter, isFirstLayer = True):
		"""寻找边距离最近的@code{item}

		我们描述一副图片的策略是：
			先为每个第二级物体(也就是次要的物体)找到第一级物体(也就是主要的物体)的参照物。
			然后再为每个第一级物体找到另一个第一级物体的参照物。
			这样，每个主要物体都能一一定位，关联到它们上的次要物体也都能得到定位。

		所以本函数的行为是：
			如果自己是第一级的物体，找的就是最近的第一级的物体。通过把自己关联到那个物体的@code{nextItem}和@code{nextdir}变量上，
			为那个物体做上标记，让其能"找到"自己。
			如果自己是第二级的物体，找的仍然是最近的第一级物体。将自己关联到那个物体的@code{dir}变量上。

		Args:
			items: 元素为@code{item}的数组。本函数会从中找到离自己"边距离"@code{item}(自己除外)
			filter: 字符串的数组。包含了满足条件的@code{item}的类别名字。也就是说，最近的那个@code{item}的类别必须在@code{item}内。
				在本例中，这个变量都是包含了所有第一级物体类别名的数组，旨在保证最近的物体是第一级物体。
			isFirstLayer: 自己是否属于第一级的物体。如果是，则
			nearestItem: 最近的@code{item}
			nearestDist: 最近的@code{item}与自己的"边距离"

		Returns:
			@code{item} or None.
			@{item}:
				只要有"最近的物体"，那么不论自己是第一级还是第二级的物体，返回的都是最近的第一级物体。
			None:
				如果@code{items}内，没有一个@{item}满足@code{filter}的条件，
				就找不到最近的满足条件的@{item}，也就没有"最近的物体",
				此时，就返回None。

		"""
		nearestItem = None
		nearestDist = -1
		for item in items:
			if item.oid == self.oid or item.category not in filter:
				continue
			elif nearestItem == None:
				nearestItem = item
				nearestDist = self.edgeDistance(item)
				continue
			
			dist = self.edgeDistance(item)
			if dist < nearestDist:
				nearestItem = item
				nearestDist = dist

		dictDirs = {
			"in front of" : self.isFrontOf, "on the right front of" : self.isRightFrontOf, "on the left front of" : self.isLeftFrontOf,\
			"on the right of" : self.isRightOf, "on the left of" : self.isLeftOf, "on" : self.isOn, "on the left behind of" : self.isLeftBehind,\
			"on the right behind of" : self.isRightBehind
		}

		if nearestItem == None:
			return None

		if isFirstLayer:
			for d in dictDirs:
				if dictDirs[d](nearestItem) == True:
					nearestItem.nextItem = self
					nearestItem.nextDir = d
					break

			self.nearestItem = nearestItem
			return nearestItem
		else:
			for d in dictDirs:
				if dictDirs[d](nearestItem) == True:
					if d not in nearestItem.dir:
						nearestItem.dir[d] = []
					nearestItem.dir[d].append(self)
					break

			self.nearestItem = nearestItem
			return nearestItem

def ReadJson(number):
	"""根据json文件的编号，处理这个文件，并返回包含Item的数组
	
	首先根据文件编号打开文件，将其字符串解码为json数组对象，
	再对每个元素提取信息，构造一个个@code{Item}，最后返回Item的数组

	Args:
		number: json文件的编号。默认json文件都是'1.json'，'4.json'这样命名的
		rawItem: 
			未经过加工处理的json对象。需要从中提取必要信息，来构造@code{Item}。
			rawItem['left'], rawItem['top'], rawItem['width'], rawItem['height']都以'px'结尾，比如333px, -20px。
		category: 这个物体的类别
		width：物体所占矩形区域的宽度。
		height： 物体所占矩形区域的高度。
		zIndex： 物体所占位置的层叠顺序。比如，2代表它在@code{zIndex}为1的物体放置在图上之后，才放置在图上
	Returns:
		一个数组。数组的每个元素都是Item。

	Exceptions:
		没有该文件，打开文件失败: 直接返回None
	"""
	path= args.json_dir + '%d.json' % number
	try:
		with open(path) as f:
			rawItems = json.load(f)
			items = []
			for rawItem in rawItems:
				category = rawItem['category']
				oid = rawItem['oid']

				left = int(rawItem['left'][0:-2])
				top = int(rawItem['top'][0:-2])
				zIndex = int(rawItem['zIndex'])
				
				width = int(rawItem['width'][0:-2])
				height = int(rawItem['height'][0:-2])
				
				position = Position(left, top, zIndex)
				size = Size(width, height)
				item = Item(category, oid, position, size)
				items.append(item)
			return items
	except Exception as e:
		return None

def main():
	p = Position(20, 10, 3)
	size = Size(40, 20)
	item = Item('cloud', p, size)

	p2 = Position(10, 20, 4)
	size2 = Size(10, 5)
	item2 = Item('sheep', p2, size2)

	items = ReadJson(1)

	degree = math.atan(1) / math.pi * 180
	print(math.atan(1) / math.pi * 180)


if __name__ == '__main__':
	main()
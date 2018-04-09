import Util
from bottle import template
import webbrowser
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--json_dir", type=str, default="results1_test/results1/", help="Json Directory")
args = parser.parse_args()

dictWeather = {
	'sun': 'It\'s a sunny day.',
	'star': 'It\'s a moonlit night.',
	'cloud': 'It\'s a cloudy day.',
	'moon': 'It\'s a starry night.',
	'daytime': 'It\'s daytime.'
}



class ImageToText(object):
	def __init__(self, items):
		"""
		
		Args:
			backgroundItem: 背景物体，一般可用于描述天气、天空和远处的山。
			inHighSky: 在高空飞行的物体
			inLowSky: 在低空飞行的物体，视为第二级物体。

			unmovable: 不可移动的静物，作为动物的分割线

			vehicleNum, plantNum: key是交通工具与植物的名字，value是它们对应的数量
		"""
		super(ImageToText, self).__init__()
		self.items = items

		self.plants = ["tree", "grass", "flower"]

		self.backgroundItem = ["mountain", "sun", "moon", "star", "cloud", "bird", "airplane", "balloon"]
		self.inHighSky = ["bird", "airplane", "balloon"]

		self.fruit = ["banana", "apple", "pear", "grape", "pineapple"]
		self.vehicle = ["bus", "car", "truck", "bicycle"]
		self.furniture = ["sofa", "chair", "dinnerware", "table", "cup", "bottle", "picnic_rug", "basket", "umbrella"]
		self.building = ["house", "fence", "bench", "road"]

		self.inLowSky = ["butterfly", "bee"]
		self.onGroundAnimal = ["dog", "cat", "chicken", "duck", "rabbit", "cow", "sheep", "horse", "pig", "people"]

		self.unmovable = self.fruit + self.furniture + self.vehicle + self.building + ["tree"]
		self.hasGrass = False

		self.vehicleNum = { vi : len([item for item in self.items if item.category == vi]) for vi in self.vehicle }
		self.plantNum = { p : len([item for item in self.items if item.category == p]) for p in self.plants }
		

	def getWeather(self):
		"""
			分析@code{items}得到关于天气的描述
		"""
		isCloudy = False
		for item in self.items:
			cate = item.category
			if cate == 'sun' or cate == 'moon':
				return dictWeather[cate]
			elif cate == 'star':
				return dictWeather['star']
			elif cate == 'cloud':
				isCloudy = True
		if isCloudy:
			return dictWeather['cloud']
		else:
			return ""

	def getDistantView(self):
		"""
			分析@code{items}得到关于山/云/鸟等等远处的风景的描述
		"""
		numMountain = 0
		numCloud = 0
		for item in self.items:
			cate = item.category
			if cate == 'mountain':
				numMountain += 1
			elif cate == 'cloud':
				numCloud += 1
			elif cate == 'sun':
				hasSun = True

		texts = []
		if numMountain is 1:
			texts.append('There is a Mountain in the distance.')
		elif numMountain >= 2:
			texts.append('There are mountains in the distance.')

		if numCloud is 1:
			texts.append('A cloud is Floating in the air.')
		elif numCloud >= 2:
			texts.append('Clouds are floating in the air.')

		backgroundText = " ".join(texts)

		# 生成高空物体的描述
		inHighSkyNum = { hi : len([item for item in self.items if item.category == hi]) for hi in self.inHighSky} # 高空物体各自的数量
		total = sum([inHighSkyNum[hi] for hi in self.inHighSky]) # 高空物体的总数
		texts = []
		for hi in inHighSkyNum:
			num = inHighSkyNum[hi]
			if num is 1:
				texts.append("a %s" % hi)
			elif num >= 2:
				texts.append("%d %ss" % (num, hi))

		highSkyText = ""
		if len(texts) >= 2:
			highSkyText =  "There are " + ", ".join(texts[:-1]) + " and " + texts[-1] + " flying in the sky." # eg. a bird, a balloon and 2 airplanes
		elif len(texts) == 1:
			if total == 1:
				highSkyText = "There is " + texts[0] + " flying in the sky."
			elif total >= 2:	
				highSkyText = "There are " + texts[0] + " flying in the sky."

		distantViewTexts = [backgroundText, highSkyText]
		return " ".join([text for text in distantViewTexts if text != ""])

	def getBucketDiscription(self):
		""" 添加关于花盆的描述

		如果出现了@code{furniture}一类的物体，说明在室内。
		如果在室内有花/树/草，则它们一般都在花盆内，就要添加这一句描述。

		Args:
			isInRoom: 判断是否在室内场景
			total: 植物的总数量

		Returns:
			字符串。
			如果在室内，则返回关于植物在花盆里的描述。如果没有植物，则返回空字符串。
			如果在室外，则返回空字符串。

		"""

		isInRoom = False
		if len([item for item in self.items if item.category in self.items]):
			isInRoom = True

		if not isInRoom:
			return ""

		texts = []
		total = sum([plantNum[plant] for plant in plantNum])
		for plant in plantNum:
			if plantNum[plant] > 1:
				texts.append(self.getPluralNoun(plant))
			elif plantNum[plant] == 1:
				texts.append(self.getSingleNoun(plant))

		text = " and ".join(texts)
		if total > 1:
			texts = "The %s are in the buckets." % text
		elif total == 1:
			texts = "The %s is in the bucket." % text
		else: # total为0，没有植物
			return ""

		return text

	def getDirTo(self, this, that):
		"""
			this->direc->taht
			如果that在this的左边，则返回on the left of
		"""
		dirs = ["on", "in front of", "on the left of", "on the right of", "behind"]
		insect = ["butterfly", "bee"]
		if this.category in self.unmovable:
			if that.category in self.unmovable:
				# 都是静物
				# 左右 前 后。后的角度判定大些
				if that.isBottomEdgeAbove(this) and that.getDegreeTo(this) >= 30 and that.center.isAbove(this.center):
					return "behind"
				elif that.getDegreeTo(this) >= 45 or that.isWithinBothSides(this):
					return "in front of"
				elif that.center.isRightOf(this.center):
					return "on the right of"
				else:
					return "on the left of"
			else: 
				# 静物与动物比
				# 上 前 左右  

				# on:
				#  车上可以有动物
				#  房子上可以有鸡/鸭
				#  bench上可以有人/猫/狗/鸟
				#  sofa上可以有猫/狗
				#  树上不会有地面动物

				# 蝴蝶, bee:
				# 只有左右，没上
				onHouseAnimal = ["chicken", "duck"] + insect
				onBenchAnimal = ["people", "cat", "dog", "bird"] + insect
				onFenceAnimal = ["chicken", "duck"] + insect
				onFurnAnimal = ["cat", "dog"] + insect


				if that.isBottomEdgeAbove(this) and that.isWithinBothSides(this):
					if this.category == "house":
						if that.category in onHouseAnimal:
							return "on"
					elif this.category == "bench":
						if that.category in onBenchAnimal:
							return "on"
					elif this.category in ["sofa", "table", "chair", "picnic_rug", "busket"]:
						if that.category in onFurnAnimal:
							return "on"
					elif this.category ==  "fence":
						if that.category in onFenceAnimal:
							return "on"
					else:
						return "on"
				if that.getDegreeTo(this) >= 35:
					return "in front of"
				if that.center.isRightOf(this.center):
					return "on the right of"
				return "on the left of"
		else:
			# 不考虑that是静物
			# 动物与动物比

			# 蝴蝶,bee只能在左/右飞
			if that.category not in insect:
				if that.getDegreeTo(this) >= 45:
					return "in front of"
			if that.center.isRightOf(this.center):
					return "on the right of"
			return "on the left of"

	def setDir(self, this, that):
		direc = self.getDirTo(this, that)
		if direc not in this.dir:
			this.dir[direc] = [that]
		else:
			this.dir[direc].append(that)

	def getPluralNoun(self, category):
		if category in ["people", "sheep"]:
			return category
		if category[-1] == "y":
			return category[:-1] + "ies"
		else:
			return category + "s"
	def getSingleNoun(self, category):
		if category == "people":
			return "person"
		return category
	def getFollowDescription(self, follows, item, wholeDir = None):
		# 描述一组动物用。item是第一个参照物，之后的参照物都是上一个描述的物体
		texts = []
		formerItem = item
		for follow in follows:
			direc = self.getDirTo(formerItem, follow)

			text = ""
			if follow.num > 1:
				text += "%d %s are" % (follow.num, self.getPluralNoun(follow.category))
			else:
				text += "A %s is" % self.getSingleNoun(follow.category)

			if follow.category in ["cow", "sheep", "horse", "rabbit"] and self.hasGrass and wholeDir != "on":
				text += " grazing"

			if formerItem.num > 1:
				text += " %s the %s." % (direc, self.getPluralNoun(formerItem.category))
			else:
				text += " %s the %s." % (direc, self.getSingleNoun(formerItem.category))

			texts.append(text)
			formerItem = follow
		return " ".join(texts)

	def getUnmovableDescription(self, item, formerItem = None):
		# 对一个静物进行描述
		texts = []
		unmovable = ""
		if item.num > 1:
			unmovable += "There are %d %s" % (item.num, self.getPluralNoun(item.category))
		else:
			unmovable += "There is a %s" % self.getSingleNoun(item.category)

		if item.category in ["bus", "car", "truck"]:
			unmovable += " running on the road"

		if formerItem == None:
			unmovable += "."
		else:
			direc = self.getDirTo(formerItem, item)
			if formerItem.num > 1:
				unmovable += " %s the %s." % (direc, self.getPluralNoun(formerItem.category))
			else:
				unmovable += " %s the %s." % (direc, self.getSingleNoun(formerItem.category))
		texts.append(unmovable)

		for direc in item.dir:
			follows = item.dir[direc]
			texts.append(self.getFollowDescription(follows, item, direc))

		return " ".join(texts)


	def getGroundItems(self):
		"""生成低空下物体的描述

		植物属于"无特征物体"，
		如果树有两颗以下，就可以作为参照物，也可寻找参照物。
		如果大于两颗，就视为"多颗"，树是相互之间无差别的，就不再以植物为参照物

		然后，先描述第一层的物体，再描述与它关联的第二层的物体
		"""

		self.mergeSameItem()

		texts = []

		# 生成植物的描述
		plantTexts = []
		if self.plantNum["flower"] >= 1:
			plantTexts.append("flowers")
		if self.plantNum["grass"] >= 1:
			self.hasGrass = True
		plantText = " and ".join(plantTexts)
		if len(plantTexts) > 0: # 有多朵花/草才进行描述
			texts.append("There are many %s." % plantText) # eg. There are many grass and flowers.

		"""
		zIndex从小到大，动物找前面的静物，静物找前面的静物
		动物与静物 左右 前 上
		动物与动物 左右 前
		静物与静物 左右 前 后。后的判定角度要大些

		上下: 
			底边在静物之上 且 中心在静物两侧中
			而且只有猫/狗能在bench上，
			任何地面动物不能在树上
		
		静物与静物:
			判断顺序：后 前 左右 
		"""

		hasUnmovable = False
		# 如果有静物，让第一个物体一定是静物。如果是动物，就把第一个静物交换过来。
		for index, item in enumerate(self.mergedItems):
			if item.category in self.unmovable and not hasUnmovable:
				hasUnmovable = True
				self.mergedItems[0], self.mergedItems[index] = self.mergedItems[index], self.mergedItems[0]

		if not hasUnmovable: # 只有动物
			# 对动物接连描述
			firstAnimal = self.mergedItems[0]
			if firstAnimal.num > 1:
				texts.append("There are %d %s." % (firstAnimal.num, self.getPluralNoun(firstAnimal.category)))
			else:
				texts.append("There is a %s." % self.getSingleNoun(firstAnimal.category))
			if len(self.mergedItems) > 1:
				texts.append(self.getFollowDescription(self.mergedItems[1:], firstAnimal))

			return " ".join(texts)

		# 把self.mergedItems处理放入items
		items = []
		lastUnMovable = None
		# 有静物
		for index, item in enumerate(self.mergedItems):

			# 是静物，则先添加到items。之后还要处理
			if item.category in self.unmovable:
				items.append(item)
				lastUnMovable = items[-1]
				continue
			
			# 是动物：
			# 	动物以最近遇到静物为参照
			# 	同时要判断两者的方向
			self.setDir(lastUnMovable, item)

		for index, item in enumerate(items): # 对静物遍历
			if index == 0:
				texts.append(self.getUnmovableDescription(item))
			else:
				formerItem = items[index - 1]
				texts.append(self.getUnmovableDescription(item, formerItem))

		return "".join(texts)
	
	def getText(self):
		"""
			分别取得关于天气，远方景象，交通工具，地面物体，以及花盆里的花的描述。
			将它们组合到一起，形成一篇完整的描述。
		"""
		weather = self.getWeather()
		distantView = self.getDistantView()
		groundItems = self.getGroundItems()
		bucketDiscription = self.getBucketDiscription()

		texts = [weather, distantView, groundItems, bucketDiscription]
		return " ".join([text for text in texts if text != ""])

	def getAvgItem(self, items):
		"""
			输入一个同类型的item数组，计算它们的平均位置和大小，合并成一个item并返回
		"""
		category = items[0].category
		oid = items[0].oid
		totalLeft = 0
		totalTop = 0
		zIndex = items[0].position.zIndex

		totalHeight = 0
		totalWidth = 0
		num = 0

		for item in items:
			totalLeft += item.position.left * item.num
			totalTop += item.position.top * item.num
			totalHeight += item.size.height * item.num
			totalWidth += item.size.width * item.num

			num += item.num

		position = Util.Position(totalLeft / num, totalTop / num, zIndex)
		size = Util.Size(totalWidth / num, totalHeight / num)

		item = Util.Item(category, oid, position, size)
		item.num = num
		return item


	def mergeSameItem(self):

		arr = ["mountain", "flower", "grass", "cloud", "sun", "bird", "airplane", "moon", "star"]
		items = [item for item in self.items if item.category not in arr]
		items = sorted(items, key = lambda item : item.position.zIndex )

		# 把边界物体合并
		# 把items处理到borderMergedItems中
		i = 0
		borderMergedItems = []
		
		while i < len(items):
			item = items[i]

			if item.category not in self.unmovable:
				borderMergedItems.append(item)
				i += 1
				continue
			borderItems = [item] # 视为同类边界的物体
			j = i + 1

			while j < len(items) and items[j].category == item.category:
				borderItems.append(items[j])
				j += 1
			borderMergedItems.append(self.getAvgItem(borderItems))
			i = j

		# 把被边界分割的同种物体合并为一个
		# 把borderMergedItems处理到splitItems中
		i = 0
		splitItems = []		
		while i < len(borderMergedItems):
			item = borderMergedItems[i]
			if item in self.unmovable:
				splitItems.append(item)
				i += 1
				continue
			movableItems = []
			toMergeItems = [item]

			j = i + 1
			while j < len(borderMergedItems) and borderMergedItems[j].category not in self.unmovable:
				thatItem = borderMergedItems[j]

				if thatItem.category != item.category:
					j += 1
					continue

				toMergeItems.append(thatItem)
				borderMergedItems.remove(thatItem)

			splitItems.append(self.getAvgItem(toMergeItems))
			borderMergedItems.remove(item)

		self.mergedItems = splitItems

def writeHTML(texts):
	"""
		把字符串生成网页在当前目录下
	"""
	message = """
	<html>
	<h1>week2 template</h1>
	<body>
	<br>
	%for i in range(0, len(items)):
	<img src={{\""""

	filePath = args.json_dir + "\%d.png "

	message2 = """"%(i+1)}} width="200px"/>
	<p>{{i+1}} : {{items[i]}}</p>
	%end
	<h2>by SYSU.Jin Zili </h2>
	</body>
	</html>"""


	

	html = template(message + filePath + message2, items=texts)
	if os.path.exists('./index.html'):
		os.remove('./index.html')
	with open("index.html", 'wb') as f:
		f.write(html.encode('utf-8'))

def main():
	texts = []
	for num in range(0, 300):
		items = Util.ReadJson(num, args.json_dir)
		if items == None:
			continue
		print(num)
		solution = ImageToText(items)
		text = solution.getText()
		print(text)
		print("----------")
		texts.append(text)
	writeHTML(texts)
	
	

if __name__ == '__main__':
	main()
		
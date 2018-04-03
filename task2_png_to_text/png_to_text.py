import Util
from bottle import template
import webbrowser
import argparse

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

			firstLayerItem, secondLayerItem:
				我们描述一副图片的策略是：先为每个第二级物体(也就是次要的物体)找到第一级物体(也就是主要的物体)的参照物。
				然后再为每个第一级物体找到另一个第一级物体的参照物。
				这样，每个主要物体都能一一定位，关联到它们上的次要物体也都能得到定位。

				所以，firstLayerItem代表第一级物体，也就是首要描述的物体。
				secondLayerItem代表第二级物体，也就是次要描述的物体。

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

		self.vehicleNum = { vi : len([item for item in self.items if item.category == vi]) for vi in self.vehicle }
		self.plantNum = {p : len([item for item in self.items if item.category == p]) for p in self.plants}
		
		# 首要描述的Item。有水果、交通工具和家具。
		self.firstLayerItem = self.fruit + self.vehicle + self.furniture + self.building + ["flower", "tree"]
		
		# 次级描述的Item。若树或花低于或等于两颗，则也可以去寻找其它参照物。
		# 若太多颗，由于它们没有特征，单独对齐位置进行描述没有什么意义。
		self.secondLayerItem = self.inLowSky + self.onGroundAnimal

		self.setLayerItems()
		self.findNearestItem()

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
			return dictWeather['daytime']

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

	def getVehicle(self):
		""" 统计各种交通工具的数量并生成相应描述

		先统计各种交通工具的数量
		再为自行车以外的交通工具生成描述。
		再为自行车生成相应描述。
		
		Args:
			total:
				自行车以外的交通工具的数量。
				当它大于1，描述要变为'There are ...' 比如 'There are 2 trucks and a bus...'


		Returns:
			字符串。关于所有交通工具的数量的描述。
		"""

		# 为自行车以外的交通工具添加相应描述
		texts = []
		for vi in self.vehicleNum:
			if vi != 'bicycle':
				num = self.vehicleNum[vi]
				if num is 1:
					texts.append("a %s" % vi)
				elif num >= 2:
					texts.append("%d %ss" % (num, vi))

		# 生成描述
		total = sum([self.vehicleNum[vi] for vi in self.vehicleNum if vi != "bicycle"]) # 自行车以外的车的总数
		text = " and ".join(texts)
		if total >= 2:
			text = "There are %s running on the road." % text 
		elif total is 1:
			text = "There is %s running on the road." % text


		# 统计自行车的数量，并添加相应描述
		if self.vehicleNum['bicycle'] is 1:
			text += 'There is a bicycle on the ground.'
		elif self.vehicleNum['bicycle'] >= 2:
			text += 'There are %d bicycles on the ground.' % self.vehicleNum['bicycle']

		return text

	def getGroundItems(self):
		"""生成低空下物体的描述

		植物属于"无特征物体"，
		如果树有两颗以下，就可以作为参照物，也可寻找参照物。
		如果大于两颗，就视为"多颗"，树是相互之间无差别的，就不再以植物为参照物

		然后，先描述第一层的物体，再描述与它关联的第二层的物体
		"""
		texts = []

		# 生成植物的描述
		plantTexts = []
		if self.plantNum["tree"] > 2:
			plantTexts.append("trees")

		if self.plantNum["flower"] > 2:
			plantTexts.append("flowers")

		if self.plantNum["grass"] >= 1:
			plantTexts.append("grass")

		plantText = " and ".join(plantTexts)
		if len(plantTexts) > 0: # 有多颗树或者花才进行描述
			texts.append("There are many %s." % plantText) # eg. There are many trees and flowers.

		groundTexts = []

		if len(self.firstLayerItems) >= 1:
			item = self.firstLayerItems[0]
			groundTexts.append("There is a %s." % item.category)
			for direction in item.dir:
				groundTexts.append(self.recDescribe(item, direction, item.dir[direction]))

		for item in self.firstLayerItems[:-1]:
			nextItem = item.nextItem
			if nextItem != None:
				groundTexts.append("A %s is %s the %s." % (nextItem.category, item.nextDir, item.category))
				for direction in nextItem.dir:
					groundTexts.append(self.recDescribe(nextItem, direction, nextItem.dir[direction]))

		texts = " ".join(texts + groundTexts)
		return "".join(texts)

	def recDescribe(self, originItem, direction, items):
		""" 按顺序为相对于第一层物体@code{originItem}的第二层物体们@code{items}进行定位描述

		由于添加顺序本身就按照@code{zIndex}, 
		可知@code{items}本身就是按照@code{zIndex}排列的。
		只需按照@code{items}的顺序一个个地描述即可。

		假设:
			direction和item不为空, items的长度至少为1

		Args:
			originItem: 作为参照物的第一层的物体。
			direction: @code{items}相对于@code{originItem}的方向
			items: 与@code{originItem}关联的第二层的物体

		"""
		texts = []

		# 描述第一个
		texts.append("A %s is %s the %s." % (items[0].category, direction, originItem.category))

		# 从第二个开始不断以前一个为参照物来描述
		for index in range(1, len(items)):
			currentItem = items[index].category
			lastItem = items[index - 1].category
			texts.append("A %s is %s the %s." % (currentItem, direction, lastItem))

		return " ".join(texts)

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
				texts.append(plant + "s")
			elif plantNum[plant] == 1:
				texts.append(plant)

		text = " and ".join(texts)
		if total > 1:
			texts = "The %s are in the buckets." % text
		elif total == 1:
			texts = "The %s is in the bucket." % text
		else: # total为0，没有植物
			return ""

		return text


	def getText(self):
		"""
			分别取得关于天气，远方景象，交通工具，地面物体，以及花盆里的花的描述。
			将它们组合到一起，形成一篇完整的描述。
		"""
		weather = self.getWeather()
		distantView = self.getDistantView()
		vehicle = self.getVehicle()
		groundItems = self.getGroundItems()
		bucketDiscription = self.getBucketDiscription()

		texts = [weather, distantView, vehicle, groundItems, bucketDiscription]
		return " ".join([text for text in texts if text != ""])

	def setLayerItems(self):
		firstLayerItems = {item for item in self.items if item.category in self.firstLayerItem}
		secondLayerItems = {item for item in self.items if item.category in self.secondLayerItem}

		self.firstLayerItems = sorted(firstLayerItems, key = lambda item : item.position.zIndex)
		self.secondLayerItems = sorted(secondLayerItems, key = lambda item : item.position.zIndex)


		# 树太多，不需要各自定位，将其从第一级物体剔除
		if self.plantNum["tree"] > 2:
			self.firstLayerItems = [item for item in self.firstLayerItems if item.category != "tree"]
		# 花太多，不需要各自定位，将其从第一级物体剔除
		if self.plantNum["flower"] > 2: 
			self.firstLayerItems = [item for item in self.firstLayerItems if item.category != "flower"]

		# 如果没有第一级物体，则第二级的物体全部提到第一级
		if len(self.firstLayerItems) == 0:
			self.firstLayerItems = self.secondLayerItems
			self.secondLayerItems = []
			self.firstLayerItem = self.secondLayerItem
			self.secondLayerItem = []

	def findNearestItem(self):
		"""
			为第一级物体与第二级物体找到最近的物体，用于作为参照物。
		"""

		for item in self.secondLayerItems: # 让每个第二级的物体从第一级物体里找参照物。
			item.findNearestItem(self.firstLayerItems, self.firstLayerItem, False)

		for item in self.firstLayerItems:
			item.findNearestItem(self.firstLayerItems, self.firstLayerItem, True)

def writeHTML(texts):
	"""
		把字符串生成网页在当前目录下
	"""
	message = """
	<html>
	<h1>week2 template</h1>
	<body>
	<br>
	%for i in range(0,len(items)):
	<img src={{\""""

	filePath = args.json_dir + "\%d.png "

	message2 = """"%(i+1)}} width="200px"/>
	<p>{{i+1}} : {{items[i]}}</p>
	%end
	<h2>by SYSU.Jin Zili </h2>
	</body>
	</html>"""


	

	html = template(message + filePath + message2, items=texts)
	with open("index.html", 'wb') as f:
		f.write(html.encode('utf-8'))

def main():
	texts = []
	for num in range(1, 100):
		items = Util.ReadJson(num, args.json_dir)
		if items == None:
			continue
		solution = ImageToText(items)
		text = solution.getText()
		texts.append(text)
	writeHTML(texts)
	
	

if __name__ == '__main__':
	main()
		
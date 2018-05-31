# -*- coding: utf-8 -*-  
import Util2

dictWeather = {
    'sun': 'It\'s a sunny day.',
    'cloud': 'It\'s a cloudy day.',
    'moon': 'It\'s a moonlit night.'
}


class ImageToText(object):
    def __init__(self, items):
        """
        Args:
            items: list，元素是Item
            index: 根据描述物体的顺序放置它们的编号
        """
        super(ImageToText, self).__init__()
        self.items: [] = items
        self.index = []

    def get_weather(self):
        """
            分析@code{items}得到关于天气的描述
        """
        is_cloudy = False
        for item in self.items:
            cate = item.category
            if cate == 'sun' or 'moon':
                return dictWeather[cate]
            elif cate == 'cloud':
                is_cloudy = True
        if is_cloudy:
            return dictWeather['cloud']
        else:
            return ""

    def get_distant_view(self):
        """
            分析@code{items}得到关于山/云/鸟等等远处的风景的描述
            默认前提： 太阳与月亮最多有一个，云可能没有，也可能有多个。
        """
        num_cloud = 0
        cloud_ids = []
        sky_item_texts = []
        sky_item_ids = []
        for item in self.items:
            cate = item.category
            index = item.id
            if cate == "cloud":
                num_cloud += 1
                cloud_ids.append(index)
            elif cate == "sun" or cate == "moon":
                sky_item_texts.append("a " + cate)
                sky_item_ids.append(index)
        texts = []
        # describe clouds
        if num_cloud == 1:
            texts.append('A cloud is Floating in the air.')
        elif num_cloud >= 2:
            texts.append('Many clouds are floating in the air.')

        num_sky_items = len(sky_item_texts)
        if num_sky_items >= 1:
            be_verb = "is" if num_sky_items == 1 else "are"
            sky_items_text = "There %s %s in the sky" % (be_verb, " and ".join(sky_item_texts))
            texts.append(sky_items_text)
        distant_view_texts = " ".join(texts)
        self.index.extend(cloud_ids + sky_item_ids)
        return distant_view_texts

    def get_ground_items(self):
        """生成低空下物体的描述
           先描述大型建筑，再描述树，最后描述动物。
           把距离较近的同种动物归为一群，描述的时候一起描述；若距离太远，就分开描述。

           """
        #  能在地面的物体: 静物、树、动物(包括鸟)
        items_can_on_ground = Util2.CATEGORIES_UNMOVABLE + Util2.CATEGORIES_TREE + Util2.CATEGORIES_MOVABLE

        ground_items = [item for item in self.items if item.category in items_can_on_ground]  # 获得地面的物体

        unmovable, trees, movable = \
            Util2.ItemCollection.get_collections(ground_items, Util2.CATEGORIES_UNMOVABLE, Util2.CATEGORIES_MOVABLE)

        print(unmovable.get_description())
        print(trees.get_description())
        print(movable.get_description())

        unmovable_description, unmovable_index = unmovable.get_description()
        trees_description, trees_index = trees.get_description()
        movable_description, movable_index = movable.get_description()

        ground_items_text = " ".join([unmovable_description, trees_description, movable_description])

        print("-----3 ground_items index----")
        print(unmovable_index, trees_index, movable_index)
        print("-----------------------------")
        self.index.extend(unmovable_index + trees_index + movable_index)
        return ground_items_text

    def get_grass_road_text(self):
        """
        :return a string that describes that all things are on grass and road.
        """
        has_grass = False  # if grass in items
        has_road = False  # if road in items
        grass_ids = []
        road_ids = []

        for item in self.items:
            category = item.category
            index = item.id
            if category == "grass":
                has_grass = True
                grass_ids.append(index)
            if category == "road":
                has_road = True
                road_ids.append(index)

        grass_road = []
        if has_grass:
            grass_road.append("grass")
        if has_road:
            grass_road.append("road")
        if has_grass or has_road:
            grass_road_text = "All things are on " + " and ".join(grass_road) + "."
        else:
            grass_road_text = ""
        self.index.extend(grass_ids)
        self.index.extend(road_ids)
        print("-------grass road index------")
        print(grass_ids + road_ids)
        print("-----------------------------")
        return grass_road_text

    def get_text(self):
        """
            分别取得关于天气，远方景象，交通工具，地面物体，以及花盆里的花的描述。
            将它们组合到一起，形成一篇完整的描述。
        """
        self.index = []
        weather = self.get_weather()
        distant_view = self.get_distant_view()
        ground_items = self.get_ground_items()
        grass_road_text = self.get_grass_road_text()

        texts = [weather, distant_view, ground_items, grass_road_text]
        return " ".join([text for text in texts if text != ""]), self.index


def png2text(pred_boxes, pred_class_ids):
    items = Util2.read(pred_boxes, pred_class_ids)
    print("items (in the order of item.oid)", [item.oid for item in items])
    solution = ImageToText(items)
    text, index = solution.get_text()
    return text, index


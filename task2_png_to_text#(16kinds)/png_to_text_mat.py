# -*- coding: utf-8 -*-  
import Util2

dictWeather = {
    'sun': 'It\'s a sunny day.',
    'cloud': 'It\'s a cloudy day.',
}


class ImageToText(object):
    def __init__(self, items):
        """
        Args:
            in_high_sky: 在高空飞行的物体
            in_low_sky: 在低空飞行的物体，视为第二级物体。

            unmovable: 不可移动的静物，作为动物的分割线

            vehicle_num, plantNum: key是交通工具与植物的名字，value是它们对应的数量
        """
        super(ImageToText, self).__init__()
        self.items = items
        self.plants = ["tree"]
        self.in_high_sky = ["bird"]
        self.vehicle = ["bus", "car"]
        self.building = ["house", "bench"]
        self.in_low_sky = ["butterfly"]
        self.on_ground_animal = ["bird", "cat", "chicken", "cow", "dog", "duck", "people", "sheep"]
        self.unmovable = self.vehicle + self.building + ["tree"]

        self.vehicle_num = {vi: len([item for item in self.items if item.category == vi]) for vi in self.vehicle}
        self.has_vehicle = len([item for item in self.items if item.category in self.vehicle]) > 0
        self.number = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",
                       "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth", "eighteenth",
                       "nineteenth", "twentieth", "twenty-first", "twenty-second", "twenty-third", "twenty-fourth",
                       "twenty-fiith", "twenty-sixth", "twenty-seventh", "twenty-eighth", "twenty-ninth", "thirtieth"]

        self.anumber = [" ", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve",
                        "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty",
                        "Twenty-one", "Twenty-two", "Twenty-three", "Twenty-four", "Twenty-five", "Twenty-six",
                        "Twenty-seven", "Twenty-eight", "Twenty-nine", "Thirty"]

    def get_weather(self):
        """
            分析@code{items}得到关于天气的描述
        """
        is_cloudy = False
        for item in self.items:
            cate = item.category
            if cate == 'sun':
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
        """
        num_cloud = 0
        num_birds = 0
        for item in self.items:
            cate = item.category
            if cate == "cloud":
                num_cloud += 1
            if cate == "bird":
                num_birds += 1

        texts = []
        # describe clouds
        if num_cloud == 1:
            texts.append('A cloud is Floating in the air.')
        elif num_cloud >= 2:
            texts.append('Many clouds are floating in the air.')

        # describe birds
        if num_birds == 1:
            texts.append("A bird is in the sky.")
        elif num_birds >= 2:
            texts.append("There are %d birds in the sky." % num_birds)
        distant_view_texts = " ".join(texts)
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

        ground_items_text = " ".join([unmovable.get_description(), trees.get_description(), movable.get_description()])
        # self.set_name_for_item_collection(CATEGORIES_TREE)
        # self.set_name_for_item_collection(CATEGORIES_MOVABLE)

        return ground_items_text

    def get_grass_road_text(self):
        """
        :return a string that describes that all things are on grass and road.
        """
        has_grass = False  # if grass in items
        has_road = False  # if road in items

        for item in self.items:
            category = item.category
            if category == "grass":
                has_grass = True
            if category == "road":
                has_road = True

        grass_road = []
        if has_grass:
            grass_road.append("grass")
        if has_road:
            grass_road.append("road")
        if has_grass or has_road:
            grass_road_text = "All things are on " + " and ".join(grass_road) + "."
        else:
            grass_road_text = ""
        return grass_road_text

    def get_text(self):
        """
            分别取得关于天气，远方景象，交通工具，地面物体，以及花盆里的花的描述。
            将它们组合到一起，形成一篇完整的描述。
        """
        weather = self.get_weather()
        distant_view = self.get_distant_view()
        ground_items = self.get_ground_items()
        grass_road_text = self.get_grass_road_text()

        texts = [weather, distant_view, ground_items, grass_road_text]
        return " ".join([text for text in texts if text != ""])


def png2text(pred_boxes, pred_class_ids):
    items = Util2.read(pred_boxes, pred_class_ids)
    print("items (in the order of item.oid)", [item.oid for item in items])
    solution = ImageToText(items)
    text = solution.get_text()
    index = []
    return text, index

#
# if __name__ == '__main__':
# 	main()
#

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

    def get_dir_to(self, this, that):
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
                    elif this.category == "fence":
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

    def set_dir(self, this, that):
        direction = self.get_dir_to(this, that)
        if direction not in this.dir:
            this.dir[direction] = [that]
        else:
            this.dir[direction].append(that)

    def get_plural_noun(self, category):
        if category in ["people", "sheep"]:
            return category
        if category[-1] == "y":
            return category[:-1] + "ies"
        else:
            return category + "s"

    def get_single_noun(self, category):
        if category == "people":
            return "person"
        return category

    def get_follow_description(self, follows, item, whole_dir=None):
        # 描述一组动物用。item是第一个参照物，之后的参照物都是上一个描述的物体
        texts = []
        formerItem = item
        for follow in follows:
            direc = self.get_dir_to(formerItem, follow)

            text = ""
            if follow.num > 1:
                text += "%s %s are" % (self.anumber[follow.num - 1], self.get_plural_noun(follow.category))
            else:

                text += "A %s is" % self.get_single_noun(follow.category)

            if follow.category in ["cow", "sheep", "horse", "rabbit"] and self.hasGrass and whole_dir != "on":
                text += " grazing"

            if formerItem.num > 1:
                text += " %s the %s." % (direc, self.get_plural_noun(formerItem.category))
            else:
                text += " %s the %s." % (direc, self.get_single_noun(formerItem.category))

            texts.append(text)
            formerItem = follow
        return " ".join(texts)

    def getUnmovableDescription(self, item, formerItem=None):
        # 对一个静物进行描述
        texts = []
        unmovable = ""
        if item.num > 1:
            unmovable += "%s %s are" % (self.anumber[item.num - 1], self.get_plural_noun(item.category))
        else:
            unmovable += "There is a %s" % self.get_single_noun(item.category)

        if item.category in ["bus", "car", "truck"]:
            unmovable += " running on the road."

        elif formerItem == None:
            unmovable += " in the distance."
        else:
            direc = self.get_dir_to(formerItem, item)
            if formerItem.num > 1:
                unmovable += " %s the %s." % (direc, self.get_plural_noun(formerItem.category))
            else:
                unmovable += " %s the %s." % (direc, self.get_single_noun(formerItem.category))
        texts.append(unmovable)

        for direc in item.dir:
            follows = item.dir[direc]
            texts.append(self.get_follow_description(follows, item, direc))

        return " ".join(texts)

    def get_ground_items(self):
        """生成低空下物体的描述
        先描述大型建筑，再描述树，最后描述动物。
        把距离较近的同种动物归为一群，描述的时候一起描述；若距离太远，就分开描述。

        """
        #  能在地面的物体: 大型物体、树、动物(包括鸟)
        items_can_on_ground = ["bench", "bus", "car", "house"] + \
                              ["tree"] + \
                              ["butterfly", "cat", "chicken", "cow", "dog", "duck", "people", "sheep", "bird"]

        ground_items = [item for item in self.items if item.category in items_can_on_ground]  # 获得地面的物体
        sorted_ground_items = sorted(ground_items, key=lambda item: item.position.top)  # 把地面的物体按位置的top来排序
        print("sorted_ground_items", [(item.oid, item.position.top) for item in sorted_ground_items])

        self.merge_same_item()
        texts = []
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

        has_unmovable = False
        # 如果有静物，让第一个物体一定是静物。如果是动物，就把第一个静物交换过来。
        for index, item in enumerate(self.merged_items):
            if item.category in self.unmovable and not has_unmovable:
                has_unmovable = True
                self.merged_items[0], self.merged_items[index] = self.merged_items[index], self.merged_items[0]

        if len(self.merged_items) == 0:
            return ""

        if not has_unmovable:  # 只有动物
            # 对动物接连描述
            first_animal = self.merged_items[0]

            if first_animal.num > 1:
                texts.append("There are %s %s." % (
                    str.lower(self.anumber[first_animal.num - 1]), self.get_plural_noun(first_animal.category)))

            else:

                texts.append("There is a %s." % self.get_single_noun(first_animal.category))
            if len(self.merged_items) > 1:
                texts.append(self.get_follow_description(self.merged_items[1:], first_animal))

            return " ".join(texts)

        # 把self.merged_items处理放入items
        items = []
        lastUnMovable = None
        # 有静物
        for index, item in enumerate(self.merged_items):

            # 是静物，则先添加到items。之后还要处理
            if item.category in self.unmovable:
                items.append(item)
                lastUnMovable = items[-1]
                continue

            # 是动物：
            # 	动物以最近遇到静物为参照
            # 	同时要判断两者的方向
            self.set_dir(lastUnMovable, item)

        for index, item in enumerate(items):  # 对静物遍历
            if index == 0:
                texts.append(self.getUnmovableDescription(item))
            else:
                formerItem = items[index - 1]
                if item.category == formerItem.category:
                    formerItem = items[index - 2]
                    texts.append(self.getUnmovableDescription(item, formerItem))
                else:
                    texts.append(self.getUnmovableDescription(item, formerItem))
        return "".join(texts)

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

    def get_avg_item(self, items):
        """
            输入一个同类型的item数组，计算它们的平均位置和大小，合并成一个item并返回
        """
        category = items[0].category
        oid = items[0].oid
        total_left = 0
        total_top = 0
        zIndex = items[0].position.zIndex

        total_height = 0
        total_width = 0
        num = 0

        for item in items:
            total_left += item.position.left * item.num
            total_top += item.position.top * item.num
            total_height += item.size.height * item.num
            total_width += item.size.width * item.num

            num += item.num

        position = Util2.Position(total_left / num, total_top / num, zIndex)
        size = Util2.Size(total_width / num, total_height / num)

        item = Util2.Item(category, oid, position, size)
        item.num = num
        return item

    def merge_same_item(self):
        """
            ???????????????
            ?????????????????????"others"????
            others?45???????????????????others?
        """
        arr = ["mountain", "flower", "grass", "cloud", "sun", "bird", "airplane", "moon", "star", "others"]

        if self.has_vehicle:
            arr.append("road")
        items = [item for item in self.items if item.category not in arr]
        items = sorted(items, key=lambda item: item.position.zIndex)

        i = 0
        border_merged_items = []

        while i < len(items):
            item = items[i]

            if item.category not in self.unmovable or item.category == "tree":  # ??????????
                border_merged_items.append(item)
                i += 1
                continue

            border_items = [item]
            j = i + 1
            while j < len(items) and items[j].category == item.category:
                border_items.append(items[j])
                j += 1
            border_merged_items.append(self.get_avg_item(border_items))
            i = j
        trees = [item for item in border_merged_items if item.category == "tree"]
        not_tree_items = [item for item in border_merged_items if item.category != "tree"]
        tree_groups = []
        while len(trees) > 0:
            tree = trees[0]
            has_found_near_tree = False
            for group in tree_groups:
                for grouped_tree in group:
                    if tree.isInteractWith(grouped_tree):
                        group.append(tree)
                        trees.remove(tree)
                        has_found_near_tree = True
                        break
                if has_found_near_tree:
                    break
            if not has_found_near_tree:
                tree_groups.append([tree])
                trees.remove(tree)
        tree_merged_items = []
        for group in tree_groups:
            tree_merged_items.append(self.get_avg_item(group))
        tree_merged_items.extend(not_tree_items)
        tree_merged_items = sorted(tree_merged_items, key=lambda item: item.position.zIndex)

        i = 0
        split_items = []
        while i < len(tree_merged_items):
            item = tree_merged_items[i]
            if item in self.unmovable:
                split_items.append(item)
                i += 1
                continue

            to_merge_items = [item]
            j = i + 1
            while j < len(tree_merged_items) and tree_merged_items[j].category not in self.unmovable:
                that_item = tree_merged_items[j]

                if that_item.category != item.category:  # ??????????
                    j += 1
                    continue

                to_merge_items.append(that_item)
                tree_merged_items.remove(that_item)

            split_items.append(self.get_avg_item(to_merge_items))
            tree_merged_items.remove(item)
        self.merged_items = split_items


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

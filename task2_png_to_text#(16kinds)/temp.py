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


from . import suffstat
from . import util


class LeafNode(object):
    def __init__(self, att_types, num_classes):
        self.suff_stats = []
        self.class_counts = {}
        for att_type in att_types:
            if att_type == "Numerical":
                ss = suffstat.SuffStatAttGaussian(num_classes)
            elif att_type == "Nominal":
                ss = suffstat.SuffStatAttDict(num_classes)
            else:
                raise("Attribute type ({}) is unknown.".format(att_type))
            self.suff_stats.append(ss)

    def add_instance(self, instance, label):
        for i, ss in enumerate(self.suff_stats):
            ss.add_value(instance[i], label)
        if label in self.class_counts:
            self.class_counts[label] += 1
        else:
            self.class_counts[label] = 0

    def check_split(self, metric, threshold, tie_break=0):
        """ Checks whether split is required.

        Args:
            metric (function: list -> float): Calculates impurity of a list.
            threshold (function: int -> float): Calculates Hoeffding bound.
            tie_break (float): Minimum allowed Hoeffding bound (default 0).

        Returns:
            None if split is not required;
            otherwise, (index of best attribute, best split point).
        """
        class_counts = self.class_counts.values()       # ATTENTION: order is not preserved
        im = metric(class_counts)          # impurity of this node
        N = sum(class_counts)              # Number of arrived instances
        best_gains = [im - ss.get_split_gain(metric) / N
                      for ss in self.suff_stats]
        (a1_index, a1_gain), (a2_index, a2_gain) = util.get_top_two(best_gains)
        e = threshold(N)
        if a1_gain - a2_gain > e or e < tie_break:
            att_value = self.suff_stats(a1_index).get_best_split_point()
            return a1_index, att_value
        else:
            return None


class DecisionNodeNumerical(object):
    def __init__(self, attribute_index, decision_value):
        self.attribute_index = attribute_index
        self.decision_value = decision_value
        self.left_child = LeafNode()
        self.right_child = LeafNode()

    def sort_down(self, instance):
        att_value = instance[self.attribute_index]
        if att_value >= self.decision_value:
            return self.right_child
        else:
            return self.left_child


class DecisionNodeNominal(object):
    def __init__(self):
        raise("Not yet implemented.")


class VFDT(object):
    """Very Fast Decision Tree
    """
    def __init__(self):
        self.root = LeafNode()

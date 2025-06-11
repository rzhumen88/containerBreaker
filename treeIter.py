from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem

def iterateTreeWidget(treeWidget: QTreeWidget):
    def iterateItem(item: QTreeWidgetItem):
        yield item
        for i in range(item.childCount()):
            child = item.child(i)
            yield from iterateItem(child)
            
    for i in range(treeWidget.topLevelItemCount()):
        topItem = treeWidget.topLevelItem(i)
        yield from iterateItem(topItem)

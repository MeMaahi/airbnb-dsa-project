"""Linked-list based data structures used by the Airbnb DSA demonstration."""

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class PropertyLinkedList:
    """Singly linked list storing property dictionaries."""
    def __init__(self):
        self.head = None
        self.size = 0

    def insert(self, property_data):
        node = Node(property_data)
        if self.head is None:
            self.head = node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = node
        self.size += 1

    def delete(self, property_id):
        current, previous = self.head, None
        while current is not None:
            if int(current.data["Property_ID"]) == int(property_id):
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                self.size -= 1
                return True
            previous, current = current, current.next
        return False

    def traverse(self):
        result, current = [], self.head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def clear(self):
        self.head = None
        self.size = 0

    def load(self, properties):
        self.clear()
        for item in properties:
            self.insert(item)


class LinkedListStack:
    """LIFO stack: most recently viewed property is at the top."""
    def __init__(self):
        self.top = None
        self.size = 0

    def push(self, item):
        node = Node(item)
        node.next = self.top
        self.top = node
        self.size += 1

    def pop(self):
        if self.top is None:
            return None
        item = self.top.data
        self.top = self.top.next
        self.size -= 1
        return item

    def peek(self):
        return self.top.data if self.top else None

    def traverse(self):
        result, current = [], self.top
        while current is not None:
            result.append(current.data)
            current = current.next
        return result


class LinkedListQueue:
    """FIFO queue: oldest booking request is at the front."""
    def __init__(self):
        self.front = None
        self.rear = None
        self.size = 0

    def enqueue(self, item):
        node = Node(item)
        if self.rear is None:
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self.size += 1

    def dequeue(self):
        if self.front is None:
            return None
        item = self.front.data
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        self.size -= 1
        return item

    def traverse(self):
        result, current = [], self.front
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

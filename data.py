"""Seed data for the Campus Brain curriculum graph.

Topics follow a typical first/second-year Data Structures syllabus.
Exam questions are SYNTHETIC (written for this project, not copied from
any university paper or private source).
"""

TOPICS = [
    ("Programming Basics", "Unit 1: Foundations"),
    ("Time Complexity", "Unit 1: Foundations"),
    ("Arrays", "Unit 1: Foundations"),
    ("Pointers", "Unit 1: Foundations"),
    ("Recursion", "Unit 1: Foundations"),
    ("Linear Search", "Unit 2: Searching and Sorting"),
    ("Binary Search", "Unit 2: Searching and Sorting"),
    ("Bubble Sort", "Unit 2: Searching and Sorting"),
    ("Insertion Sort", "Unit 2: Searching and Sorting"),
    ("Merge Sort", "Unit 2: Searching and Sorting"),
    ("Quick Sort", "Unit 2: Searching and Sorting"),
    ("Linked Lists", "Unit 3: Linear Structures"),
    ("Stacks", "Unit 3: Linear Structures"),
    ("Queues", "Unit 3: Linear Structures"),
    ("Hashing", "Unit 3: Linear Structures"),
    ("Trees", "Unit 4: Trees"),
    ("Binary Search Trees", "Unit 4: Trees"),
    ("AVL Trees", "Unit 4: Trees"),
    ("Heaps", "Unit 4: Trees"),
    ("Graph Representation", "Unit 5: Graphs"),
    ("BFS", "Unit 5: Graphs"),
    ("DFS", "Unit 5: Graphs"),
    ("Shortest Path", "Unit 5: Graphs"),
]

# topic -> list of topics that must be learned first
PREREQS = {
    "Time Complexity": ["Programming Basics"],
    "Arrays": ["Programming Basics"],
    "Pointers": ["Programming Basics"],
    "Recursion": ["Programming Basics"],
    "Linear Search": ["Arrays"],
    "Binary Search": ["Arrays", "Time Complexity"],
    "Bubble Sort": ["Arrays"],
    "Insertion Sort": ["Arrays"],
    "Merge Sort": ["Recursion", "Arrays"],
    "Quick Sort": ["Recursion", "Arrays"],
    "Linked Lists": ["Pointers", "Arrays"],
    "Stacks": ["Linked Lists", "Arrays"],
    "Queues": ["Linked Lists", "Arrays"],
    "Hashing": ["Arrays"],
    "Trees": ["Linked Lists", "Recursion"],
    "Binary Search Trees": ["Trees", "Binary Search"],
    "AVL Trees": ["Binary Search Trees"],
    "Heaps": ["Trees", "Arrays"],
    "Graph Representation": ["Arrays", "Linked Lists"],
    "BFS": ["Graph Representation", "Queues"],
    "DFS": ["Graph Representation", "Stacks", "Recursion"],
    "Shortest Path": ["BFS", "Heaps"],
}

# (question text, marks, year, topics tested)
QUESTIONS = [
    ("Explain why binary search needs a sorted array and derive its time complexity.", 5, 2023, ["Binary Search", "Time Complexity"]),
    ("Implement a stack using a linked list.", 8, 2022, ["Stacks", "Linked Lists"]),
    ("Write a recursive function for factorial and analyse its complexity.", 5, 2023, ["Recursion", "Time Complexity"]),
    ("Compare bubble sort and insertion sort with an example.", 5, 2022, ["Bubble Sort", "Insertion Sort"]),
    ("Sort 8 numbers with merge sort and show each merge step.", 8, 2024, ["Merge Sort", "Recursion"]),
    ("Explain the partition step of quick sort with an example.", 5, 2023, ["Quick Sort", "Arrays"]),
    ("Reverse a singly linked list.", 5, 2024, ["Linked Lists", "Pointers"]),
    ("Implement a queue using two stacks.", 8, 2023, ["Queues", "Stacks"]),
    ("Explain collision handling in hashing: chaining and open addressing.", 8, 2022, ["Hashing"]),
    ("Insert 10, 20, 30, 40, 50 into an empty BST and draw the tree.", 5, 2024, ["Binary Search Trees"]),
    ("Show the AVL rotations after inserting 30, 20, 10.", 8, 2023, ["AVL Trees", "Binary Search Trees"]),
    ("Build a max-heap from an array and show the heapify steps.", 8, 2024, ["Heaps", "Arrays"]),
    ("Write inorder, preorder and postorder traversals of a binary tree.", 5, 2022, ["Trees", "Recursion"]),
    ("Represent a graph as an adjacency list and an adjacency matrix.", 5, 2023, ["Graph Representation"]),
    ("Run BFS on a given graph and list the visit order.", 5, 2024, ["BFS", "Queues"]),
    ("Run DFS with a stack and compare it with the recursive version.", 8, 2023, ["DFS", "Stacks", "Recursion"]),
    ("Apply Dijkstra's algorithm on a weighted graph from source A.", 10, 2024, ["Shortest Path", "Heaps"]),
    ("Explain big-O with examples of O(1), O(n) and O(n log n).", 5, 2022, ["Time Complexity"]),
    ("Differences between arrays and linked lists, with memory diagrams.", 5, 2023, ["Arrays", "Linked Lists"]),
    ("Do a linear search and analyse best, average and worst case.", 5, 2022, ["Linear Search", "Time Complexity"]),
    ("Convert an infix expression to postfix using a stack.", 8, 2024, ["Stacks"]),
    ("Explain pointers and dynamic memory allocation with an example.", 5, 2022, ["Pointers"]),
]

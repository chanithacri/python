def alice_books(n, actions):
    unread_books = []
    read_books = []
    for action in actions:
        if action.startswith('BUY'):
            _, book = action.split(" ", 1)
            unread_books.append(book)
        elif action == 'READ':
            read_books.append(unread_books.pop())
    for book in read_books:
        print(book)


alice_books(4, ['BUY Pride and Prejudice', 'BUY Anna Karenina', 'READ', 'BUY Hamlet'])
alice_books(8, ['BUY Pride and Prejudice', 'BUY Anna Karenina', 'READ', 'BUY Hamlet', 'BUY Pride and Prejudice', 'BUY Anna Karenina', 'READ', 'BUY Hamlet'])

def phase(func):
    def wrapper(*args, **kwargs):
        width = 25
        text = func.__name__.upper()
        formatted_text = f"#{' ' * ((width - len(text) - 2) // 2)}{text}{' ' * ((width - len(text) - 2) // 2)}#"
        border = '#' * width
        print(border)
        print(formatted_text)
        print(border)
        return func(*args, **kwargs)
    return wrapper
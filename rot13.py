def rot_13(string):
    """Function to apply rot13 algo to input string"""

    space = "abcdefghijklmnopqrstuvwxyz"
    rot_str = ""
    for char in string:
        if char in space:
            char = space[(space.index(char)+13)%26]
            # print char
        else:
            #for caps
            if char.lower() in space:
                char = space[(space.index(char.lower())+13)%26].upper()
        rot_str = rot_str + char

    return rot_str

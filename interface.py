from database import *
from tabulate import tabulate

choice_prompt = """\
1. Add a box type
2. Show box types
3. Load box to container
4. Show container
5. Summary Report
X. Close\
"""


# helper function to get valid input
def get_numeric_input(called: str) -> str:
    valid_input = False
    n = None

    while not valid_input:
        n = input(f"\nPlease enter the {called}: ")
        try:
            n = float(n)
            valid_input = True
        except ValueError:
            print("Please provide a numeric input")
    
    return n


# calls db helper to return all box types from the db
def display_box_types():
    boxes = database_get_all_boxes(connection)
    """
    example:
    boxes = [
        Box(id=1, name='b1', height=2.0, width=2.0, length=2.0),
        Box(id=2, name='b2', height=1.0, width=1.0, length=5.0)
    ]
    """
    print("\n" + tabulate(boxes, 
        headers=["box_id", "box_name", "height", "width", "length"],
        tablefmt="psql") + "\n"
    )


def add_box_menu():
    box_name = input("Please enter a name for the box: ")
    box_height = get_numeric_input("box's height in meters")
    box_width = get_numeric_input("box's width height in meters")
    box_length = get_numeric_input("box's length height in meters")

    # add information to database
    database_add_box(connection, (box_name, box_height, box_width, box_length))


def load_box_menu():
    # ask for box name
    user_input = input("Enter the name of the box: ")
    # validate box exists
    box = get_box(connection, name=user_input)
    if not box:
        print("\nA box by that name coult not be found.\n")
    else:
        box_dimensions = box.height * box.width * box.length
        container_input = input("Enter the id of the container to load box to: ")
        # check capacity total volume < 30 (our own constraints)
        container = get_container(connection, container_input)
        if container is None or (container.occupied_volume + box_dimensions <= 30):
            # add the box to the freight
            add_box_to_container(connection, box.id, container_input)
            container = get_container(connection, container_input)
            # print(container)
            print("\n" + tabulate([container],
                headers=["container_id", "occupied_volume"],
                tablefmt="psql") + "\n"
            )
        else:
            print(f"Container {container_input} does not have enough space for box {user_input}")

def main_menu():
    valid_choices = [x[0] for x in choice_prompt.split("\n")]
    while(True):
        print(choice_prompt)

        print("\n================")
        user_input = input("Your choice: ")
        print("================\n")

        if user_input.lower() == "x":
            print("Goodbye!")
            print("================\n")
            break

        if user_input not in valid_choices:
            raise Exception("Please select one of: ", valid_choices)

        print("\n================")
        print(f"Choice {user_input} selected")
        print("================\n")

        match user_input:
            case '1':
                add_box_menu()
            case '2':
                display_box_types()
            case '3':
                load_box_menu()
            case '4':
                pass
            case '5':
                pass

if __name__ == "__main__":
    connection = create_database_and_tables(filename="freight_prod.db")
    # seed_data(connection)
    main_menu()
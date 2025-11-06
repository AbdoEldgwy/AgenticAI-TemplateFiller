import json

# Load the service data from the JSON file
with open('service.json', 'r', encoding='utf-8') as f:
    services = json.load(f)


# Define the functions to retrieve and update service data
def get_services() -> list:
    """Retrieve a list of all available services.
    returns:
        list: A list of dictionaries containing service details.
    """
    return services

def get_services_by_index (index: int) -> dict:
    """Retrieve service details based on the provided service index.

    Args:
        index (int): The index of the service to retrieve.

    Returns:
        dict: The service details if found, otherwise an empty dictionary.
    """
    for s in services:
        if s["index"] == index:
            return s
    return {"error": "Service not found"}

def update_service_prices(service_name: str, new_price: float) -> dict:
    """
    Update a service price by name.

    Args:
        service_name (str): The service name intended by the user
        new_price (float): The new price of the service name intended
    """
    for s in services:
        if s["name"] == service_name:
            s["price"] = new_price
            return {"message": f"تم تعديل سعر الخدمة {service_name} إلى {new_price} ريال ✅"}
    return {"error": "Service not found"}


def fill_template(template_path: str = 'docTemp/الموافق.docx' ):
    from TemplateManager import ManageTemp
    '''
    Fill and save the document template with provided all user data.
     Args:
        template_path (str): Path to the document template.
    '''
    manager = ManageTemp(template_path, services)
    manager.rendering()

    return {"message": "Template filled saved ✅"}
document.addEventListener('DOMContentLoaded', fetchItems);

async function fetchItems() {
    try {
        const response = await fetch('/items');
        if (!response.ok) throw new Error('Failed to fetch items');

        const data = await response.json();
        renderItems(data.items);
    } catch (error) {
        console.error(error.message);
    }
}

function renderItems(items) {
    const itemsList = document.getElementById('itemList');
    itemsList.innerHTML = '';

    items.forEach(item => {
        const itemElement = createItemElement(item);
        itemsList.appendChild(itemElement);
    });
}

function createItemElement(item) {
    const itemElement = document.createElement('li');
    itemElement.classList.add('item');

    const itemName = document.createElement('span');
    itemName.innerText = item.item_name;
    itemName.classList.add('item-name');

    const itemQuantity = document.createElement('span');
    itemQuantity.innerText = `Quantity: ${item.quantity}`;
    itemQuantity.classList.add('item-quantity');

    const deleteButton = createButton('Delete', 'delete-btn', () => deleteItem(item.item_id));
    const removeButton = createButton('Remove', 'remove-btn', () => removeQuantity(item.item_id, 1));

    // Add margin between buttons
    deleteButton.style.marginRight = '5px';

    itemElement.appendChild(itemName);
    itemElement.appendChild(itemQuantity);
    itemElement.appendChild(deleteButton);
    itemElement.appendChild(removeButton);

    return itemElement;
}

function createButton(text, className, onClickHandler) {
    const button = document.createElement('button');
    button.innerText = text;
    button.classList.add(className);
    button.onclick = onClickHandler;
    return button;
}

async function addItem() {
    const itemName = document.getElementById('itemName').value;
    const itemQuantity = document.getElementById('itemQuantity').value;
    const message = document.getElementById('message');

    try {
        if (!itemName || !itemQuantity) {
            throw new Error('Please enter both item name and quantity.');
        }

        const response = await fetch(`/items/${itemName}/${itemQuantity}`, {
            method: 'POST'
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail);
        }

        message.innerText = '';
        fetchItems();
        document.getElementById('itemName').value = '';
        document.getElementById('itemQuantity').value = '';
    } catch (error) {
        message.innerText = error.message;
    }
}

async function deleteItem(itemId) {
    try {
        const response = await fetch(`/items/${itemId}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete item');
        
        fetchItems();
    } catch (error) {
        console.error(error.message);
    }
}

async function removeQuantity(itemId, quantity) {
    try {
        const response = await fetch(`/items/${itemId}/${quantity}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to remove quantity');
        
        fetchItems();
    } catch (error) {
        console.error(error.message);
    }
}

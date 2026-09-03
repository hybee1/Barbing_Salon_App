/* ==========================================================
   salon-manager-inventory.js
   Levelz Cuts - Inventory Manager
========================================================== */

let inventoryInitialized = false;


/* ==========================================================
   INITIALIZE
========================================================== */

function initInventoryPage() {

    if (inventoryInitialized) {

        loadInventory();

        return;

    }

    inventoryInitialized = true;

    const createButton =
        document.getElementById("createInventoryBtn");

    createButton?.addEventListener(
        "click",
        showInventoryCreateForm
    );

    loadInventory();

}


/* ==========================================================
   LOAD INVENTORY
========================================================== */

async function loadInventory() {

    const container =
        document.getElementById("inventoryContainer");

    if (!container) return;

    container.innerHTML = `
        <div class="inventory-loading">
            Loading inventory...
        </div>
    `;

    try {

        const [itemsResponse, summaryResponse] =
            await Promise.all([

                apiRequest(
                    "/inventory/items/"
                ),

                apiRequest(
                    "/inventory/items/summary/"
                )

            ]);

        const items =
            itemsResponse.results || itemsResponse;

        renderInventory(
            items,
            summaryResponse
        );

    } catch (error) {

        console.error(
            "Failed to load inventory:",
            error
        );

        container.innerHTML = `
            <div class="error-message">
                Unable to load inventory.
            </div>
        `;

    }

}


/* ==========================================================
   RENDER INVENTORY
========================================================== */

function renderInventory(
    items,
    summary
) {

    const container =
        document.getElementById(
            "inventoryContainer"
        );

    if (!container) return;

    container.innerHTML = `

        <div class="stats">

            <article class="stat-card">

                <div>
                    <small>Active Items</small>
                    <h2>
                        ${summary.total_items ?? 0}
                    </h2>
                </div>

                <i class="fa-solid fa-boxes-stacked"></i>

            </article>


            <article class="stat-card">

                <div>
                    <small>Low Stock</small>
                    <h2>
                        ${summary.low_stock_items ?? 0}
                    </h2>
                </div>

                <i class="fa-solid fa-triangle-exclamation"></i>

            </article>


            <article class="stat-card">

                <div>
                    <small>Stock Value</small>
                    <h2>
                        ${formatMoney(
                            summary.total_stock_value
                        )}
                    </h2>
                </div>

                <i class="fa-solid fa-naira-sign"></i>

            </article>

        </div>


        <div class="table-scroll">

            <table>

                <thead>

                    <tr>

                        <th>Item</th>
                        <th>Category</th>
                        <th>Type</th>
                        <th>Quantity</th>
                        <th>Reorder Level</th>
                        <th>Cost / Unit</th>
                        <th>Status</th>
                        <th>Action</th>

                    </tr>

                </thead>

                <tbody>

                    ${
                        items.length
                        ? items.map(
                            renderInventoryRow
                        ).join("")
                        : `
                            <tr>
                                <td colspan="8">
                                    No inventory items found.
                                </td>
                            </tr>
                        `
                    }

                </tbody>

            </table>

        </div>

    `;

    bindInventoryActions();

}


/* ==========================================================
   INVENTORY ROW
========================================================== */

function renderInventoryRow(item) {

    const lowStock =
        item.is_low_stock;

    return `

        <tr>

            <td>
                <strong>
                    ${escapeHtml(item.name)}
                </strong>
            </td>

            <td>
                ${escapeHtml(
                    item.category_name || "-"
                )}
            </td>

            <td>
                ${escapeHtml(
                    item.item_type_display || "-"
                )}
            </td>

            <td class="${lowStock ? "low-stock" : ""}">
                ${item.quantity}
                ${escapeHtml(item.unit || "")}
            </td>

            <td>
                ${item.reorder_level}
            </td>

            <td>
                ${formatMoney(
                    item.cost_per_unit
                )}
            </td>

            <td>
                ${renderInventoryStatus(item)}
            </td>

            <td>

                <button
                    type="button"
                    class="inventory-action-btn"
                    data-action="stock-in"
                    data-id="${item.id}">
                    Stock In
                </button>

                <button
                    type="button"
                    class="inventory-action-btn"
                    data-action="stock-out"
                    data-id="${item.id}">
                    Stock Out
                </button>

            </td>

        </tr>

    `;

}


/* ==========================================================
   STATUS
========================================================== */

function renderInventoryStatus(item) {

    if (item.is_low_stock) {

        return `
            <span class="status-badge warning">
                Low Stock
            </span>
        `;

    }

    if (item.status === "active") {

        return `
            <span class="status-badge success">
                Active
            </span>
        `;

    }

    return `
        <span class="status-badge">
            ${escapeHtml(
                item.status_display || item.status
            )}
        </span>
    `;

}


/* ==========================================================
   ACTIONS
========================================================== */

function bindInventoryActions() {

    document
        .querySelectorAll(
            ".inventory-action-btn"
        )
        .forEach(button => {

            button.addEventListener(
                "click",
                () => {

                    const id =
                        button.dataset.id;

                    const action =
                        button.dataset.action;

                    if (action === "stock-in") {

                        stockInInventory(id);

                    }

                    if (action === "stock-out") {

                        stockOutInventory(id);

                    }

                }
            );

        });

}


/* ==========================================================
   STOCK IN
========================================================== */

async function stockInInventory(itemId) {

    const quantity =
        prompt("Enter quantity to add:");

    if (quantity === null) return;

    const numericQuantity =
        Number(quantity);

    if (
        !Number.isFinite(numericQuantity)
        || numericQuantity <= 0
    ) {

        alert(
            "Enter a valid quantity greater than zero."
        );

        return;

    }

    try {

        await apiRequest(
            `/inventory/items/${itemId}/stock-in/`,
            "POST",
            {
                quantity:
                    numericQuantity
            }
        );

        await loadInventory();

    } catch (error) {

        console.error(
            "Stock-in failed:",
            error
        );

        alert(
            getApiErrorMessage(error)
        );

    }

}


/* ==========================================================
   STOCK OUT
========================================================== */

async function stockOutInventory(itemId) {

    const quantity =
        prompt("Enter quantity to remove:");

    if (quantity === null) return;

    const numericQuantity =
        Number(quantity);

    if (
        !Number.isFinite(numericQuantity)
        || numericQuantity <= 0
    ) {

        alert(
            "Enter a valid quantity greater than zero."
        );

        return;

    }

    const reason =
        prompt(
            "Reason: consumed, damaged, expired, transferred or other"
        );

    if (!reason) return;

    try {

        await apiRequest(
            `/inventory/items/${itemId}/stock-out/`,
            "POST",
            {
                quantity:
                    numericQuantity,

                reason:
                    reason
            }
        );

        await loadInventory();

    } catch (error) {

        console.error(
            "Stock-out failed:",
            error
        );

        alert(
            getApiErrorMessage(error)
        );

    }

}


/* ==========================================================
   CREATE ITEM
========================================================== */

function showInventoryCreateForm() {

    const container =
        document.getElementById(
            "inventoryContainer"
        );

    if (!container) return;

    container.insertAdjacentHTML(
        "afterbegin",
        `

        <div class="card inventory-form-card">

            <div class="card-header">

                <h3>New Inventory Item</h3>

                <button
                    type="button"
                    id="cancelInventoryForm">
                    Cancel
                </button>

            </div>

            <form id="inventoryCreateForm">

                <div class="filter-actions">

                    <input
                        type="text"
                        id="inventoryName"
                        placeholder="Item name"
                        required>

                    <input
                        type="number"
                        id="inventoryCategory"
                        placeholder="Category ID"
                        required>

                    <select
                        id="inventoryItemType"
                        required>

                        <option value="">
                            Item Type
                        </option>

                        <option value="equipment">
                            Equipment
                        </option>

                        <option value="consumable">
                            Consumable
                        </option>

                        <option value="supply">
                            Supply
                        </option>

                    </select>

                    <input
                        type="number"
                        step="0.01"
                        min="0"
                        id="inventoryQuantity"
                        placeholder="Quantity"
                        value="0">

                    <input
                        type="text"
                        id="inventoryUnit"
                        placeholder="Unit"
                        value="unit">

                    <input
                        type="number"
                        step="0.01"
                        min="0"
                        id="inventoryReorderLevel"
                        placeholder="Reorder level"
                        value="0">

                    <input
                        type="number"
                        step="0.01"
                        min="0"
                        id="inventoryCost"
                        placeholder="Cost per unit"
                        value="0">

                    <input
                        type="text"
                        id="inventorySupplier"
                        placeholder="Supplier">

                    <input
                        type="text"
                        id="inventoryStorage"
                        placeholder="Storage location">

                </div>

                <button
                    type="submit"
                    class="gold-btn">
                    Save Inventory Item
                </button>

            </form>

        </div>

        `
    );

    document
        .getElementById(
            "cancelInventoryForm"
        )
        ?.addEventListener(
            "click",
            () => {

                loadInventory();

            }
        );

    document
        .getElementById(
            "inventoryCreateForm"
        )
        ?.addEventListener(
            "submit",
            createInventoryItem
        );

}


/* ==========================================================
   CREATE INVENTORY ITEM
========================================================== */

async function createInventoryItem(event) {

    event.preventDefault();

    const data = {

        name:
            document.getElementById(
                "inventoryName"
            ).value.trim(),

        category:
            document.getElementById(
                "inventoryCategory"
            ).value,

        item_type:
            document.getElementById(
                "inventoryItemType"
            ).value,

        quantity:
            document.getElementById(
                "inventoryQuantity"
            ).value || 0,

        unit:
            document.getElementById(
                "inventoryUnit"
            ).value.trim() || "unit",

        reorder_level:
            document.getElementById(
                "inventoryReorderLevel"
            ).value || 0,

        cost_per_unit:
            document.getElementById(
                "inventoryCost"
            ).value || 0,

        supplier:
            document.getElementById(
                "inventorySupplier"
            ).value.trim(),

        storage_location:
            document.getElementById(
                "inventoryStorage"
            ).value.trim()

    };

    try {

        await apiRequest(
            "/inventory/items/",
            "POST",
            data
        );

        await loadInventory();

    } catch (error) {

        console.error(
            "Creating inventory item failed:",
            error
        );

        alert(
            getApiErrorMessage(error)
        );

    }

}


/* ==========================================================
   MONEY
========================================================== */

function formatMoney(value) {

    const number =
        Number(value || 0);

    return `₦${number.toLocaleString(
        "en-NG",
        {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    )}`;

}


/* ==========================================================
   ESCAPE HTML
========================================================== */

function escapeHtml(value) {

    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}


/* ==========================================================
   API ERROR
========================================================== */

function getApiErrorMessage(error) {

    if (!error) {

        return "An unexpected error occurred.";

    }

    if (typeof error === "string") {

        return error;

    }

    if (error.detail) {

        return error.detail;

    }

    try {

        return Object.entries(error)
            .map(
                ([field, messages]) =>
                    `${field}: ${
                        Array.isArray(messages)
                            ? messages.join(", ")
                            : messages
                    }`
            )
            .join("\n");

    } catch {

        return "An unexpected error occurred.";

    }

}

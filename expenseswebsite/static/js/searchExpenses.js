const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
const noResults = document.querySelector(".no-results");
const tbody = document.querySelector(".table-body");

let currentSearchValue = '';
let currentAbortController = null;
tableOutput.style.display = "none";

function debounce(func, delay) {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

const performSearch = debounce(async (searchValue) => {
  if (searchValue === currentSearchValue) return;
  currentSearchValue = searchValue;

  if (currentAbortController) {
    currentAbortController.abort();
  }
  currentAbortController = new AbortController();

  console.log("Search value:", searchValue);

  if (searchValue.trim().length > 0) {
    console.log("Searching...");
    paginationContainer.style.display = "none";
    tbody.innerHTML = "";
    appTable.style.display = "none";
    noResults.style.display = "none";

    try {
      const response = await fetch("/search-expenses", {
        body: JSON.stringify({ searchText: searchValue }),
        method: "POST",
        signal: currentAbortController.signal
      });
      const data = await response.json();
      console.log("Server response:", data);

      if (data.length === 0) {
        noResults.style.display = "block";
        tableOutput.style.display = "none";
      } else {
        noResults.style.display = "none";
        tableOutput.style.display = "block";
        const fragment = document.createDocumentFragment();
        data.forEach((item) => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${item.amount}</td>
            <td>${item.category}</td>
            <td>${item.description}</td>
            <td>${item.date}</td>
            <td><a href="/edit-expense/${item.id}" class="btn btn-secondary btn-sm">Edit</a></td>
          `;
          fragment.appendChild(tr);
        });
        tbody.appendChild(fragment);
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Fetch aborted');
      } else {
        console.error('Fetch error:', error);
      }
    }
  } else {
    console.log("Empty search, showing default view");
    tableOutput.style.display = "none";
    noResults.style.display = "none";
    appTable.style.display = "block";
    paginationContainer.style.display = "block";
  }
  console.log("Render complete");
}, 300);

searchField.addEventListener("input", (e) => performSearch(e.target.value));

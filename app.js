// App Theme Management
const themeToggleBtn = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');
const themeText = document.getElementById('theme-text');

// Function to set theme
function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  
  if (theme === 'dark') {
    if (themeIcon) themeIcon.setAttribute('data-lucide', 'sun');
    if (themeText) themeText.textContent = 'Light Mode';
  } else {
    if (themeIcon) themeIcon.setAttribute('data-lucide', 'moon');
    if (themeText) themeText.textContent = 'Dark Mode';
  }
  
  // Re-run lucide icons to replace svg
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Toggle Theme Event
if (themeToggleBtn) {
  themeToggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
  });
}

// Load Persisted Theme
const savedTheme = localStorage.getItem('theme') || 'light';
setTheme(savedTheme);


// Homepage Recipes Rendering (Only on index.html)
const recipeGrid = document.getElementById('recipe-grid');
const searchInput = document.getElementById('search-input');
const categoryContainer = document.getElementById('category-container');
const recipeCountEl = document.getElementById('recipe-count');

let allRecipes = [];

// Fetch Recipes Data
async function loadRecipes() {
  if (!recipeGrid) return; // Not on home page
  
  try {
    const response = await fetch('recipes.json');
    if (!response.ok) {
      throw new Error('Failed to fetch recipes database.');
    }
    allRecipes = await response.json();
    
    // Sort recipes by date descending (newest first)
    allRecipes.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    renderRecipes(allRecipes);
    updateRecipeCount(allRecipes.length);
  } catch (error) {
    console.error('Error loading recipes database:', error);
    recipeGrid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px; border: 1px dashed var(--border); border-radius: var(--radius-md);">
        <i data-lucide="info" style="color: var(--primary); width: 48px; height: 48px; margin-bottom: 12px;"></i>
        <h3 style="margin-bottom: 8px;">No Recipes Available Yet</h3>
        <p style="color: var(--text-muted);">The daily automation pipeline is initializing. Check back shortly!</p>
      </div>
    `;
    if (window.lucide) window.lucide.createIcons();
  }
}

// Render Recipes Grid
function renderRecipes(recipesList) {
  if (!recipeGrid) return;
  
  if (recipesList.length === 0) {
    recipeGrid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px;">
        <p style="color: var(--text-muted);">No recipes match your search criteria. Try another keyword!</p>
      </div>
    `;
    return;
  }
  
  recipeGrid.innerHTML = recipesList.map(recipe => {
    return `
      <article class="recipe-card" data-id="${recipe.id}">
        <div class="recipe-card-img-wrapper">
          <img src="${recipe.imageUrl}" alt="${recipe.title}" class="recipe-card-img" loading="lazy">
          <span class="recipe-badge">${recipe.category}</span>
        </div>
        <div class="recipe-card-content">
          <div class="recipe-meta-top">
            <span>By GourmetDaily Chef</span>
            <span>${formatDate(recipe.date)}</span>
          </div>
          <h3 class="recipe-card-title"><a href="${recipe.fileName}">${recipe.title}</a></h3>
          <p class="recipe-card-desc">${recipe.description}</p>
          <div class="recipe-meta-bottom">
            <span class="recipe-time">
              <i data-lucide="clock" style="width: 16px; height: 16px; color: var(--primary);"></i>
              ${recipe.prepTime + recipe.cookTime} mins
            </span>
            <span class="recipe-difficulty">
              <i data-lucide="award" style="width: 16px; height: 16px; color: var(--secondary);"></i>
              ${recipe.difficulty}
            </span>
          </div>
        </div>
      </article>
    `;
  }).join('');
  
  // Re-run lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Update count label
function updateRecipeCount(count) {
  if (recipeCountEl) {
    recipeCountEl.textContent = `Showing ${count} delicious recipe${count === 1 ? '' : 's'}`;
  }
}

// Date formatter
function formatDate(dateString) {
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('en-US', options);
}

// Filter and Search Event Handlers
if (recipeGrid) {
  // Search Input Handler
  searchInput.addEventListener('input', (e) => {
    filterAndSearchRecipes();
  });
  
  // Category Buttons Handler
  categoryContainer.addEventListener('click', (e) => {
    const clickedBtn = e.target.closest('.category-btn');
    if (!clickedBtn) return;
    
    // Toggle active class
    document.querySelectorAll('.category-btn').forEach(btn => btn.classList.remove('active'));
    clickedBtn.classList.add('active');
    
    filterAndSearchRecipes();
  });
}

function filterAndSearchRecipes() {
  const query = searchInput.value.toLowerCase().trim();
  const activeBtn = document.querySelector('.category-btn.active');
  const category = activeBtn ? activeBtn.getAttribute('data-category') : 'all';
  
  const filtered = allRecipes.filter(recipe => {
    const matchesSearch = recipe.title.toLowerCase().includes(query) || 
                          recipe.description.toLowerCase().includes(query) ||
                          recipe.ingredients.some(ing => ing.toLowerCase().includes(query));
                          
    const matchesCategory = category === 'all' || recipe.category.toLowerCase() === category.toLowerCase();
    
    return matchesSearch && matchesCategory;
  });
  
  renderRecipes(filtered);
  updateRecipeCount(filtered.length);
}

// Page load initialization
document.addEventListener('DOMContentLoaded', () => {
  loadRecipes();
  
  // Handle ingredient checklist persistence (For recipe pages)
  const checklistItems = document.querySelectorAll('.ingredient-item input[type="checkbox"]');
  if (checklistItems.length > 0) {
    const pageId = window.location.pathname.split('/').pop() || 'recipe';
    
    // Load checklist state from localStorage
    const savedChecklist = JSON.parse(localStorage.getItem(`checklist_${pageId}`)) || {};
    
    checklistItems.forEach((checkbox, index) => {
      checkbox.checked = !!savedChecklist[index];
      
      checkbox.addEventListener('change', () => {
        savedChecklist[index] = checkbox.checked;
        localStorage.setItem(`checklist_${pageId}`, JSON.stringify(savedChecklist));
      });
    });
  }
});

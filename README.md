# TUBES-2-BERKOM
### ATURAZA 💰
ATURAZA is a robust and interactive Command Line Interface (CLI) application designed to help users manage their personal finances effectively. Built with Python, it combines the simplicity of a terminal with a beautiful, rich user interface to track income, expenses, and financial health.

### Key Features
<ul>
  <li>Transaction Management</li>
  <li>Comprehensive History</li>
  <li>Random Pick</li>
  <li>Visual Statistics: 
    <ul>
      <li>7-Day Expense Trend (ASCII Bar Chart)</li>
      <li>Cash Flow Analysis</li>
      <li>Daily Average Spending</li>
      <li>Most Frequent & Highest Spending categories</li>
    </ul>    
  </li>
  <li>Financial Planning</li>
</ul>

### TechStack
<ul>
  <li>Language: Python 3.13</li>
  <li>Database: SQLite3 (Local storage, auto-generated) </li>
  <li>Libraries: 
    <ul>
      <li>Rich</li>
      <li>Questionary</li>
      <li>Pyfiglet</li>
    </ul>
  </li>  
</ul>


## Installation
# Prerequisites
Make sure you have Python 3.7+ installed on your system.
1. Clone the Repository
   ```sh
   git clone https://github.com/yourusername/aturaza.git
   cd aturaza
   ```
2. Install Dependencies
   You can install the required libraries using ```pip```:
   ```sh
   pip install questionary rich pyfiglet prompt_toolkit
   ```
3. Run the Application
   ```sh
   python aturaza.py
   ```
   Note: The application will automatically generate a data.db file in the same directory upon the first launch.

## Usage Guide
1. Navigation: Use the Arrow Keys (⬆️ ⬇️) to navigate menus and Enter to select.
2. Input:
   <ul>
     <li>Date: You can type "hari ini" for today or just press enter, or use format DD/MM/YYYY.</li>
     <li>Nominal: Enter numbers only (no dots or commas).</li>
   </ul>
3. Autocomplete: When typing a location/subject, the app suggests previous entries to save time.
4. Edit/Delete: Go to the History menu, select Edit Data, choose a transaction, and follow the prompts.



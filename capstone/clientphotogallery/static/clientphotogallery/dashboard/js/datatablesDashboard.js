window.addEventListener('DOMContentLoaded', event => {
    // Simple-DataTables
    // https://github.com/fiduswriter/Simple-DataTables/wiki

    const datatablesClientSelections = document.getElementById('datatablesClientSelections');
    if (datatablesClientSelections) {
        new simpleDatatables.DataTable(datatablesClientSelections);
    }
});

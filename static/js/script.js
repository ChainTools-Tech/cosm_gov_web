document.addEventListener('DOMContentLoaded', function () {
    // Get the filtering controls
    var proposalTypeFilter = document.getElementById("proposal-type-filter");
    var statusFilter = document.getElementById("status-filter");
    var chainNameFilter = document.getElementById("chain-name-filter");
    var chainIdFilter = document.getElementById("chain-id-filter");

    // Get all table rows
    var rows = Array.from(document.querySelectorAll("#proposal-table tbody tr"));

    // Add event listeners to the filtering controls
    proposalTypeFilter.addEventListener("change", applyFilters);
    statusFilter.addEventListener("change", applyFilters);
    chainNameFilter.addEventListener("change", applyFilters);
    chainIdFilter.addEventListener("change", applyFilters);

    function applyFilters() {
        var selectedProposalType = proposalTypeFilter.value;
        var selectedStatus = statusFilter.value;
        var selectedChainName = chainNameFilter.value;
        var selectedChainId = chainIdFilter.value;

        rows.forEach(function (row) {
            var chainName = row.cells[0].textContent.trim();
            var chainId = row.cells[1].textContent.trim();
            var proposalType = row.cells[3].textContent.trim();
            var status = row.cells[5].textContent.trim();

            var proposalTypeMatch = selectedProposalType === "" || proposalType === selectedProposalType;
            var statusMatch = selectedStatus === "" || status === selectedStatus;
            var chainNameMatch = selectedChainName === "" || chainName === selectedChainName;
            var chainIdMatch = selectedChainId === "" || chainId === selectedChainId;

            if (proposalTypeMatch && statusMatch && chainNameMatch && chainIdMatch) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
    }
});

$(document).ready(function() {

    /* DASHBOARD */
    if (window.location.pathname === "/dashboard/") {
        /* Funcion DataTable para el dashboard */
        const $table = $('.table');
        if ($table.length) {
            const $tbody = $table.find('tbody');
            const $noRecordsRow = $tbody.find('tr:contains("No hay registros disponibles")');
            if ($noRecordsRow.length) {
                console.log('La tabla contiene el mensaje: "No hay registros disponibles".');
            } else {
                $table.DataTable({
                    responsive: true,
                    autoWidth: false,
                    language: {
                        url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json", // Traducción al español
                        search: "Búsqueda:",
                        paginate: {
                            first: "Primero",
                            last: "Último",
                            next: "Siguiente",
                            previous: "Anterior"
                        },
                        info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
                        infoEmpty: "Mostrando 0 registros",
                        infoFiltered: "(filtrado de _MAX_ registros totales)"
                    },
                    dom: '<"row mb-3"<"col-sm-12 col-md-6"B><"col-sm-12 col-md-6"f>>' +
                        '<"row"<"col-sm-12"tr>>' +
                        '<"row mt-3"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
                    buttons: [
                        'copy', 'excel', 'csv', 'pdf', 'print', 'colvis' // Botones de exportación y visibilidad de columnas
                    ],
                    lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
                    pageLength: 10,
                    order: [[0, 'asc']],
                    columnDefs: [
                        { orderable: false, targets: '_all' }
                    ],
                    stripeClasses: ['table-striped', 'table-hover'],
                    pagingType: 'full_numbers',
                    fixedHeader: true,
                    stateSave: true,
                });
            }
        }
    }

    /* REGISTRO MODIFICAR */
    if (/^\/dashboard\/\d+\/edit$/.test(window.location.pathname)) {
        // Inicializa Select2 en el select con la clase 'select2'
        $('select.select2').select2({
            placeholder: "Selecciona una colección",  // Texto predeterminado
            allowClear: true  // Permite borrar la selección
        });
    }
    
});

/* REGISTRO DETALLE */
document.addEventListener("DOMContentLoaded", function () {
    const disabledButton = document.getElementById("disabled-approve-btn");

    if (disabledButton) {
        // Mostrar un tooltip al pasar el mouse
        disabledButton.addEventListener("mouseenter", function () {
            showMessage(disabledButton, "Colección no asignada");
        });

        // Mostrar un mensaje al hacer clic
        disabledButton.addEventListener("click", function (e) {
            e.preventDefault(); // Previene la acción del enlace
            alert("Colección no asignada");
        });
    }

    // Función para mostrar un mensaje tipo tooltip
    function showMessage(element, message) {
        element.setAttribute("data-bs-toggle", "tooltip");
        element.setAttribute("data-bs-placement", "top");
        element.setAttribute("title", message);

        // Inicia el tooltip usando Bootstrap si está disponible
        if (typeof bootstrap !== "undefined") {
            const tooltip = bootstrap.Tooltip.getOrCreateInstance(element);
            tooltip.show();
        }
    }
});
// File: menus/static/menus/admin/js/hide_fields.js
// This script dynamically shows/hides form fields in the MenuItem admin based on Link Type.

(function($) {
    $(function() { // Ensure DOM is ready

        // Cache selectors for performance
        var $linkTypeSelect = $('.admin-link-type-select'); // Our custom class from formfield_for_dbfield
        
        // Find the parent div of link_page and link_url fields, assuming Django's default structure
        // This might need adjustment based on your admin rendering structure (as_p, as_table, manual rendering)
        var $linkPageField = $('#id_link_page').closest('.form-row, .form-group, .field-link_page'); 
        var $linkUrlField = $('#id_link_url').closest('.form-row, .form-group, .field-link_url');

        // Initial state on page load
        function toggleFields() {
            var selectedLinkType = $linkTypeSelect.val();

            // Hide all link-specific fields by default
            $linkPageField.hide();
            $linkUrlField.hide();

            // Show fields based on selected link type
            if (selectedLinkType === 'page') {
                $linkPageField.show();
            } else if (selectedLinkType === 'url') {
                $linkUrlField.show();
            }
            // Add other conditions for new dynamic types if they need specific fields
        }

        // Attach event listener for changes
        $linkTypeSelect.on('change', toggleFields);

        // Run on page load
        toggleFields();
    });
})(django.jQuery); // Use django.jQuery to ensure compatibility with Django's admin
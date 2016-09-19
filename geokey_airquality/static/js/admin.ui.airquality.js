$(document).ready(function() {
    var project;
    var loader = $('#loader');
    var categories = $('#categories');
    var projectLoadedEvent = new Event('project-loaded');

    // Displays an error message
    function error(message) {
        var modal = $('#modal-error');

        modal.find('.modal-body p').text(message);
        modal.modal('show');
    }

    // When user changes project...
    $('select#project').on('change', function() {
        var val = $(this).val();

        // Clear and hide the structure of categories and fields
        categories.addClass('hidden');
        categories.find('.fields').addClass('hidden');
        categories.find('select').each(function() {
            $(this).children('option:not(:first)').remove();
        });
        categories.find('.form-group').removeClass('has-error').find('.help-block').remove();

        // If project is selected, build structure of categories
        if (val) {
            // Show loader
            loader.removeClass('hidden');

            Control.Ajax.get('airquality/projects/' + val,
                function(response) {
                    project = response;

                    // Do not let to use the project, if it does not have 5 categories
                    if (project.categories.length < 5) {
                        error('Project must have at least 5 active categories. Please select another project from the list.');
                    } else {
                        // For each project's categories leave only text and lookup fields
                        $.each(project.categories, function(index, category) {
                            category.textFields = [];
                            category.lookupFields = [];

                            $.each(category.fields, function(index, field) {
                                if (field.fieldtype == 'TextField') {
                                    category.textFields.push(field);
                                } else if (field.fieldtype == 'LookupField') {
                                    category.lookupFields.push(field);
                                }
                            });
                        });

                        // Make options for select field of project's categories
                        var options = [];

                        $.each(project.categories, function(index, category) {
                            options.push('<option value="' + category.id + '">' + category.name + ' (' + category.textFields.length + '+' + category.lookupFields.length + ')</option>');
                        });

                        // Populate categories with project's categories
                        categories.find('select.category').each(function() {
                            $(this).append(options);
                        });

                        // Show ready categories
                        categories.removeClass('hidden');

                        // Inform window that the project has been loaded
                        window.dispatchEvent(projectLoadedEvent);
                    }

                    // Hide loader
                    loader.addClass('hidden');
                },
                function(response) {
                    // Show error message
                    if (response.responseJSON && response.responseJSON.error) {
                        error('The server returned an error message: ' + response.responseJSON.error);
                    } else {
                        error('An unknown error occurred. Please try again.');
                    }

                    // Make sure no project is selected
                    $('select#project').prop('selectedIndex', 0);

                    // Hide loader
                    loader.addClass('hidden');
                }
            );
        }
    });

    // When user changes category...
    categories.find('select.category').each(function() {
        var i;

        $(this).on('change', function() {
            // Clear and hide the structure of fields
            var fields = $(this).closest('.panel').find('.fields');
            fields.addClass('hidden');
            fields.find('select').each(function() {
                $(this).children('option:not(:first)').remove();
            });
            fields.find('.form-group').removeClass('has-error').find('.help-block').remove();

            // Get the actual category
            var category;

            for (i = 0; i < project.categories.length; i++) {
                if ($(this).val() == project.categories[i].id) {
                    category = project.categories[i];
                }
            }

            if (category.textFields.length < 10) {
                // Do not let to use the category, if it does not have 10 text fields
                error('Category must have at least 10 active text fields. Please select another category from the list (number of total active text fields is displayed in the parantheses).');

                // Make sure no category is selected
                $(this).prop('selectedIndex', 0);
            } else if (category.lookupFields.length < 1) {
                // Do not let to use the category, if it does not have 1 lookup field
                error('Category must have at least 1 active select box field. Please select another category from the list (number of total active select box fields is displayed in the parantheses).');

                // Make sure no category is selected
                $(this).prop('selectedIndex', 0);
            } else {
                // Make options for select field of category's fields
                var textOptions = [];
                var lookupOptions = [];

                for (i = 0; i < category.textFields.length; i++) {
                    textOptions.push('<option value="' + category.textFields[i].id + '">' + category.textFields[i].name + '</option>');
                }

                for (i = 0; i < category.lookupFields.length; i++) {
                    lookupOptions.push('<option value="' + category.lookupFields[i].id + '">' + category.lookupFields[i].name + '</option>');
                }

                // Populate fields with category's fields
                $(this).closest('.panel').find('select.field').each(function() {
                    if ($(this).hasClass('made_by_students')) {
                        $(this).append(lookupOptions);
                    } else {
                        $(this).append(textOptions);
                    }
                });

                // Show ready fields
                fields.removeClass('hidden');
            }
        });
    });

    // When user changes "Diffusion tube made by students field"...
    categories.find('select.made_by_students').each(function() {
        $(this).on('change', function() {
            console.log('a')
        });
    });

    // If project is already set...
    var data = $('body').data();

    if (data.project) {
        // Set project as selected
        $('select#project').val(data.project).trigger('change');
        delete data.project;

        window.addEventListener('project-loaded', function(event) {
            // Set categories and fields as selected
            var fields = {};

            $.each(data, function(key, value) {
                if (key.indexOf('_field_') === -1) {
                    $('select#' + key.replace('category_', '')).val(value).trigger('change');
                } else {
                    fields[key] = value;
                }
            });

            $.each(fields, function(key, value) {
                key = key.replace('category_', '').replace('field_', '').split('__');
                $('select#' + key[0]).closest('.panel').find('select[name="' + key[1] + '"]').val(value).trigger('change');
            });
        }, false);
    }
});

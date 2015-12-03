$(document).ready(function() {
    var project;
    var categories = $('#categories');

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
            var url = 'airquality/projects/' + val;

            Control.Ajax.get(url,
                function(response) {
                    project = response;

                    // Do not let to use the project, if it does not have 5 categories
                    if (project.categories.length < 5) {
                        error('Project must have at least 5 active categories. Please select another project from the list.');
                    } else {
                        // For each project's categories leave only text fields
                        for (var i = 0; i < project.categories.length; i++) {
                            var textFields = [];

                            for (var x = 0; x < project.categories[i].fields.length; x++) {
                                if (project.categories[i].fields[x].fieldtype == 'TextField') {
                                    textFields.push(project.categories[i].fields[x]);
                                }
                            }

                            project.categories[i].fields = textFields;
                        }

                        // Make options for select field of project's categories
                        var options = [];

                        for (var i = 0; i < project.categories.length; i++) {
                            options.push('<option value="' + project.categories[i].id + '">' + project.categories[i].name + ' (' + project.categories[i].fields.length + ')</option>');
                        }

                        // Populate categories with project's categories
                        categories.find('select.category').each(function() {
                            $(this).append(options);
                        });

                        // Show ready categories
                        categories.removeClass('hidden');
                    }
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
                }
            );
        }
    });

    // When user changes category...
    categories.find('select.category').each(function() {
        $(this).on('change', function() {
            // Clear and hide the structure of fields
            var fields = $(this).parent().parent().find('.fields');
            fields.addClass('hidden');
            fields.find('select').each(function() {
                $(this).children('option:not(:first)').remove();
            });
            fields.find('.form-group').removeClass('has-error').find('.help-block').remove();

            // Get the actual category
            var category;

            for (var i = 0; i < project.categories.length; i++) {
                if ($(this).val() == project.categories[i].id) {
                    category = project.categories[i];
                }
            }

            // Do not let to use the category, if it does not have 10 text fields
            if (category.fields.length < 10) {
                error('Category must have at least 10 active text fields. Please select another category from the list (number of total active text fields is displayed in the parantheses).');

                // Make sure no category is selected
                $(this).prop('selectedIndex', 0);
            } else {
                // Make options for select field of category's fields
                var options = [];

                for (var i = 0; i < category.fields.length; i++) {
                    options.push('<option value="' + category.fields[i].id + '">' + category.fields[i].name + '</option>');
                }

                // Populate fields with category's fields
                $(this).parent().parent().find('select.field').each(function() {
                    $(this).append(options);
                });

                // Show ready fields
                fields.removeClass('hidden');
            }
        });
    });
});


$(document).ready(function() {
    if($('#hdn_tab_active').val()=='2'){
        $('#form_secondary_education').append( $('#pnl_files>div') );
    }
    $('#pnl_assimilation_criteria').css('visibility', 'hidden').css('display','none');
    if($("#slt_nationality").val()!="-1"){
        $.ajax({
            url: "/admission/country?nationality=" + $("#slt_nationality").val()
        }).then(function(data) {
            if (data.european_union) {
                $('#pnl_assimilation_criteria').css('visibility', 'hidden').css('display','none');
            }else{
                $('#pnl_assimilation_criteria').css('visibility', 'visible').css('display','block');
            }
        });
    }

    $('#txt_admission_exam_date').val('');
    $('#txt_admission_exam_institution').val('');
    $('[id^="rdb_admission_exam_type_"]').prop( "checked", false);
    $('#txt_admission_exam_type_other').val('');
    $('#txt_admission_exam_type_other').prop( "disabled", true);
    $('#chb_admission_exam_type').prop( "checked", false);

    populate_exam_admin();

    if($('#hdn_current_application_id').val() != '') {
        $('#txt_offer_year_id').val($('#hdn_application_offer_year_id').val());
        $('#slt_offer_type').val($('#hdn_application_grade_type_id').val());
        display_known_offer($('#hdn_application_offer_year_id').val());
    }

    $('#slt_criteria_5').trigger('change');
    //If information message is on the screen it will disappear after 5s
    $('#message_info').fadeOut(5000);
    $('#msg_validation_diploma').fadeOut(5000);


    $("#pnl_existing_files").on('click', '#bt_delete_document_file', function () {
        // needed otherwise the click event isn't handled
        click_bt_delete_document_file();
    });

    $("#pnl_assimilation_criteria").on('click', "button[id^='btn_load_assimilation_doc_']" , function (event) {

        var target = $(event.target);
        var id = target.attr("id");
        // needed otherwise the click event isn't handled
        if(id.startsWith('btn_load_assimilation_doc_') ){
            //upload for assimilation
            var pos = id.indexOf('_id_');
            var description = id.substring(pos+4);
            update_description(description, target);
            display_existing_files(description);
        }
    });
    change_menu();

    $('body').ajaxComplete(function(e, xhr, settings) {
        if (xhr.status == 278) {
            alert('kk');
            window.location.href = xhr.getResponseHeader("Location").replace(/\?.*$/, "?next="+window.location.pathname);
        }
    });


});

const PROFILE_TAB = 0;
const DEMAND_TAB = 1;
const PREREQUISITES_TAB = 2;
const CURRICULUM_TAB = 3;
const ACCOUNTING_TAB = 4;
const SOCIOLOGICAL_SURVEY_TAB = 5;
const ATTACHMENTS_TAB = 6;
const SUBMISSION_TAB = 7;

function set_following_tab(next_tab){
    $('[id^="hdn_following_"]').val(next_tab);
}

$('[id^="lnk_profil_next_step"]').click(function() {
    change_menu();
    $('#txt_message_error_profile_up').css('visibility', 'hidden').css('display','none');
    if (! valid(DEMAND_TAB)){
        return false;
    }
    $('#hdn_tab_applications_status').val('True');
    set_following_tab(DEMAND_TAB);
    return true;
});

$("#lnk_application_tab").click(function() {
    change_menu();
    if(! valid(DEMAND_TAB)){
        return false;
    }
    if ($('#hdn_application_id').val()){
        $('#slt_offer_type option').each(function(){
            if($(this).attr('value')==$('#hdn_application_grade').val()){
                $(this).prop('selected', true);
            }
        });
        $('#slt_domain option').each(function(){
            if($(this).attr('value')==$('#hdn_application_parent_domain_id').val()){
                $(this).prop('selected', true);
            }
        });
    }
    set_following_tab(DEMAND_TAB);
});

$("#btn_modify_picture").click(function(event) {
    update_description('ID_PICTURE', $(event.target));
    display_existing_files('ID_PICTURE');
});

$("#btn_modify_id_document").click(function(event) {
    update_description('ID_CARD',$(event.target));
    display_existing_files('ID_CARD');
});

$("#txt_birth_date").blur(function() {
    var value = $("#txt_birth_date").val();
    $("#msg_error_birth_date").find("label").remove();
    if (isDate(value)){
        $("#msg_error_birth_date").find("label").remove();
    }else{
        $("#msg_error_birth_date").append("<label>Invalid</label>");
    }
});

function isDate(txtDate){
    var currVal = txtDate;
    if(currVal == '')
        return false;

    var rxDatePattern = /^(\d{1,2})(\/|-)(\d{1,2})(\/|-)(\d{4})$/; //Declare Regex
    var dtArray = currVal.match(rxDatePattern); // is format OK?

    if (dtArray == null)
        return false;

    //Checks for mm/dd/yyyy format.
    dtDay = dtArray[1];
    dtMonth= dtArray[3];
    dtYear = dtArray[5];

    if (dtMonth < 1 || dtMonth > 12) {
        return false;
    } else if (dtDay < 1 || dtDay> 31) {
        return false;
    } else if ((dtMonth==4 || dtMonth==6 || dtMonth==9 || dtMonth==11) && dtDay ==31) {
        return false;
    } else if (dtMonth == 2) {
        var isleap = (dtYear % 4 == 0 && (dtYear % 100 != 0 || dtYear % 400 == 0));
        if (dtDay> 29 || (dtDay ==29 && !isleap)) {
            return false;
        }
    }
    if (dtYear< 1900){
        return false;
    }
    return true;
}

function valid(next_tab){
    $('#txt_message_error_profile_up').css('visibility', 'hidden').css('display','none');
    $('#txt_message_error_profile_up').html('');

    if($("#hdn_tab_active").val() == PROFILE_TAB.toString()){
        if(!valid_profile_navigation()){
            return false;
        }
    }else{
        if($("#hdn_tab_active").val() == DEMAND_TAB.toString() && next_tab != PROFILE_TAB ){
            if(!valid_offer()){
                $('#txt_message_error_profile_up').css('visibility', 'visible').css('display','block');
                $('#txt_message_error_profile_up').text(gettext('invalid_data'));
                return false;
            }
        }
    }


    if($("#hdn_tab_active").val()==PROFILE_TAB.toString()){
        if (! valid_profile()){
            $('#txt_message_error_profile_up').css('visibility', 'visible').css('display','block');
            $('#txt_message_error_profile_up').text(gettext('invalid_data'));
            return false;
        }
    }

    return true;
}

function valid_profile(){
    $('#txt_message_error_profile_up').css('visibility', 'hidden').css('display','none');
    $('#txt_message_error_profile_up').html('');

    if (valid_profile_data()){
        if( !valid_profile_navigation() ){
            $('#txt_message_error_profile_up').css('visibility', 'visible').css('display','block');
            $('#txt_message_error_profile_up').text(gettext('invalid_data'));
            return false;
        }else{
            return true;
        }
    }else{
        return false;
    }
}

$("#lnk_diploma_tab").click(function() {
    $('#txt_message_error_profile_up').css('visibility', 'hidden').css('display','none');
    $('#txt_message_error_profile_up').html('');
    $('#form_secondary_education').append( $('#pnl_files>div') );
    if (! valid(PREREQUISITES_TAB)) {
        return false;
    }
    set_following_tab(PREREQUISITES_TAB);
});

$("#lnk_curriculum_tab").click(function() {
    if (! valid(CURRICULUM_TAB)){
        return false;
    }
    set_following_tab(CURRICULUM_TAB);
});

$("#lnk_accounting_tab").click(function() {
    if (! valid(ACCOUNTING_TAB)){
        return false;
    }
    set_following_tab(ACCOUNTING_TAB);
});

$("#lnk_sociological_tab").click(function() {
    if (! valid(SOCIOLOGICAL_SURVEY_TAB)){
        return false;
    }
    set_following_tab(SOCIOLOGICAL_SURVEY_TAB);
});

$("#lnk_attachments_tab").click(function() {
    if (! valid(ATTACHMENTS_TAB)){
        return false;
    }
    set_following_tab(ATTACHMENTS_TAB);
});

$("#lnk_submission_tab").click(function() {
    if (! valid(SUBMISSION_TAB)){
        return false;
    }
    set_following_tab(SUBMISSION_TAB);
});

$("#lnk_profile_tab").click(function() {
    if($("#hdn_tab_active").val() != DEMAND_TAB.toString()) {
        if (! valid(PROFILE_TAB)) {
            return false;
        }
    }
    if($("#hdn_tab_active").val() != DEMAND_TAB.toString()) {
        set_following_tab(PROFILE_TAB);
    }

});

function valid_offer() {
    $('#txt_message_error_profile_up').css('visibility', 'hidden').css('display','none');
    $('#txt_message_error_profile_up').html('');
    if ($("#txt_offer_year_id").val()==''
        || ($('#rdb_offer_national_coverage_degree_true').prop("checked") == false && $('#rdb_offer_national_coverage_degree_false').prop("checked") == false) ){
        $("#txt_message_error_offer_up").text(gettext('msg_next_offer'));
        $('#txt_message_error_offer_up').css('visibility', 'visible').css('display','block');
        $("#txt_message_error_offer_down").text(gettext('msg_next_offer'));
        $('#txt_message_error_offer_down').css('visibility', 'visible').css('display','block');
        return false;
    }
    return true;
}

$('[id^="lnk_next_offer_step"]').click(function() {
    change_menu();
    $('#demande_next_tab').val(PREREQUISITES_TAB);
    return offer_steps(2);
});

$('[id^="lnk_previous_offer_step"]').click(function() {
    $('#demande_next_tab').val(PROFILE_TAB);
    change_menu();
    $('#form_secondary_education').append( $('#pnl_files>div') );
    return offer_steps(PROFILE_TAB);
});

function offer_steps(next_tab){
    $('#txt_message_error_offer_up').css('visibility', 'hidden').css('display','none');
    $('#txt_message_error_offer_down').css('visibility', 'hidden').css('display','none');
    if (! valid(next_tab)){
        return false;
    }
    $('#hdn_tab_applications_status').val('True');
    if( $('#demande_next_tab').val()!=''){
        next_tab=$('#demande_next_tab').val();
    }
    set_following_tab(next_tab);
    return true;
}

function display_known_offer(offer_year_id){
    ajax_grade_choice($('#hdn_application_grade_type_id').val());
    $('#slt_domain').val($('#hdn_application_parent_domain_id').val());
    ajax_offers($('#hdn_application_grade_type_id').val(),$('#hdn_application_offer_year_id').val());
    display_dynamic_form(offer_year_id);
    ajax_static_questions(offer_year_id,$('#hdn_applied_to_sameprogram').val(),$('#hdn_coverage_access_degree').val(),$('#hdn_started_samestudies').val(),$('#hdn_valuation_possible').val());
}

//***************************
//Assimilation criteria
//***************************
$( "input[name^='assimilation_criteria_']" ).click(function(event) {
    //One of the criteria has been checked as true or false
    var target = $(event.target);
    var id = target.attr("id");

    if(id.endsWith("_false")){
        var criteria = id.replace('assimilation_criteria_','');
        criteria = criteria.replace('_false','');
        $("#pnl_criteria_"+criteria).css('visibility', 'hidden').css('display','none');
    }

    if(id.endsWith("_true")){
        //Hide all pnl_criteria to let only one visible
        $('[id^="pnl_criteria_"]').each(function(){
            var target_pnl = $(this);
            var id_pnl = target_pnl.attr("id");

            var pos = id_pnl.indexOf('pnl_criteria_');
            var criteria_id = id_pnl.substring(pos+13);

            if ($('input[type=radio][name=assimilation_criteria_'+criteria_id+']:checked').attr('value') == 'true'){
                if(id != 'assimilation_criteria_'+criteria_id+'_true'){
                    $('#assimilation_criteria_'+criteria_id+'_false').prop( "checked", true);
                }
            }
            $(this).css('visibility', 'hidden').css('display','none');
        });
        var criteria = id.replace('assimilation_criteria_','');
        criteria = criteria.replace('_true','');
        $("#pnl_criteria_"+criteria).css('visibility', 'visible').css('display','block');
        $("#slt_criteria_5").val("");
    }
});

$("#slt_criteria_5").change(function(event) {
    $('[id^="pnl_criteria_bis_CRITERIA"]').each(function(){
        $(this).remove();
    });

    var target = $(event.target);
    var id = target.attr("id");
    var selected_criteria = $("#slt_criteria_5").val();
    var id_to_clone = "#pnl_criteria_"+selected_criteria;
    var div_cloned =$(id_to_clone).clone();
    var id_cloned_div = "pnl_criteria_bis_"+selected_criteria;
    div_cloned.attr("id",id_cloned_div);
    div_cloned.css('visibility', 'visible').css('display','block');
    div_cloned.appendTo("#pnl_other_criteria");
    var span = "<div>"+ gettext('concerned_person')+"</div>";
    $('#'+id_cloned_div+' .panel-heading').append(span);
});
//***************************
//Assimilation criteria - end
//***************************

//***************************
//File upload
//***************************
function update_description(description, elt){
    $('#hdn_description').val(description);
    $('#lbl_description_label').text(gettext(description.toLowerCase()));
    $('#txt_file').val('');
}

$("#txt_file").on("change", function(){
    var file = this.files[0];
    fileName = file.name;
    $("#hdn_filename").val(fileName);
});

$('[id^="bt_load_doc_"]').click(function(event) {
    var target = $(event.target);
    var id = target.attr("id");
    var pos = id.indexOf('bt_load_doc_');
    var description = id.substring(pos+12);
    update_description(description, target);
    display_existing_files(description);
});

$("#bt_upload_document").click(function(event) {
    var target = $(event.target);
    var id = target.attr("id");
    var form = target.form;

    var description = $("#hdn_description").val();
    //Clear existing fields
    $('#hdn_file_'+$("#txt_file").val()).remove();
    $('#hdn_file_name_'+description).remove();
    $('#hdn_file_description_'+description).remove();
    var fileSelect = document.getElementById('txt_file');
    var files = fileSelect.files;
    var file = files[0];
    var data = new FormData();
    data.append('description', description);
    data.append('storage_duration', 0);
    data.append('content_type',file.type);
    data.append('filename', $("#txt_file").val());
    data.append('application_id', $("#hdn_current_application_id").val());


    var accepted_types = ['application/csv',
        'application/doc',
        'application/pdf',
        'application/xls',
        'application/xlsx',
        'application/xml',
        'application/zip',
        'image/jpeg',
        'image/gif',
        'image/png',
        'text/html',
        'text/plain'];
    if(file){
        if ($.inArray(file.type,accepted_types) >= 0){
            data.append('file', file);
            $.ajax({
                url: "{% url 'save_uploaded_file' %}",
                enctype: 'multipart/form-data',
                type: 'POST',
                data : data,
                processData: false,
                contentType: false,
                complete: function(xhr, statusText){
                    if(xhr.status=='0'){
                        //problem occured
                        $('#pnl_admission_error').remove();
                        var msg_error = jQuery('<div class="alert alert-danger" id="pnl_admission_error">'+ gettext('error_occured')+'</span>');
                        $('#pnl_admission_errors').append(msg_error);
                        return false;
                    }
                    update_upload_btn_class(file, description);
                }

            });
            // update_upload_btn_class(file, description);
            return true;
        }else{
            display_existing_files(description);
            $("#txt_file").val('')
            $('#pnl_upload_error').remove();
            var msg_error = jQuery('<div class="alert alert-danger" id="pnl_upload_error">'+ file.name + ' : ' +gettext('invalid_content_type')+ ' </span>');
            $('#pnl_modal_upload').append(msg_error);
            event.preventDefault();
            event.stopImmediatePropagation();
            return false;
        }
    }else{
        display_existing_files(description);
        $("#txt_file").val('')
        $('#pnl_upload_error').remove();
        var msg_error = jQuery('<div class="alert alert-warning" role="alert" id="pnl_upload_error">' +gettext('select_file')+ ' </div>');
        $('#pnl_modal_upload').append(msg_error);
        event.preventDefault();
        event.stopImmediatePropagation();
        return false;
    }


});

//***************************
//File upload - end
//***************************
function display_existing_files(description){
    // To clear the div
    $("#pnl_existing_files").html('')
    $("#pnl_existing_files").find("a")
        .remove()
        .end()
    $("#pnl_modal_upload").find("span").remove();
    application = $('#hdn_current_application_id').val();
    var url_str = "/admission/document_application?description=" + description + "&application=" + application;
    if(description == 'ID_CARD' || description == 'ID_PICTURE'){
        url_str = "/admission/document?description=" + description;
    }
    $.ajax({
        url: url_str
    }).then(function(data) {
        if(data.length > 0 ){
            $('#pnl_existing_files').append("<br>");
            $('#pnl_existing_files').append('<span style="text-decoration:underline;">Existing file :</span>');
            $.each(data, function(key, value) {
                var url = build_url('upload/download/', value.id);
                $('#pnl_existing_files').append("<br>");
                $('#pnl_existing_files').append($("<a></a>").attr("href", url)
                    .attr("target","_blank")
                    .append(value.file_name));
                var bt = jQuery('<input  id="hdn_delete_document_file" type="hidden" value="'+value.id+'">');
                $('#pnl_existing_files').append(bt);
                $('#pnl_existing_files').append('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;');
                bt = jQuery('<button type="submit" id="bt_delete_document_file" class="btn btn-default" data-dismiss="modal"><span class="glyphicon glyphicon-trash"></span></button>');
                $('#pnl_existing_files').append(bt);
            });
        }
    });
}

function build_url(url_begin, value){
    /*Todo try to use django url directly in href - Leila*/
    var loc = location.href;
    var count = 0;
    var pos = loc.indexOf('/admission/');

    pos = pos + 12;
    while ( pos != -1 ) {
        count++;
        pos = loc.indexOf( "/",pos + 1 );
    }
    count=count-1;
    var url = url_begin + value;
    var cpt = 0;
    while (cpt< count){
        url = "../" + url;
        cpt = cpt + 1;
    }
    return url;
}

function click_bt_delete_document_file(){
    var document_file_id = $('#hdn_delete_document_file').val();
    var description = $("#hdn_description").val();
    var data = new FormData();
    data.append('document_file_id', document_file_id);
    $.ajax({
        url: "{% url 'delete_document_file' %}",
        type: 'POST',
        data : data,
        processData: false,
        contentType: false

    });
    update_upload_btn_class('',description);
    return true;
}

function update_upload_btn_class(file, description){
    if(file != ''){
        if(description == 'ID_PICTURE'){
            $('#btn_modify_picture').attr('title', gettext('change_document'));
            $('#btn_modify_picture').attr('class', 'btn btn-success ');
            $('#spn_modify_picture').attr('class', 'glyphicon glyphicon-ok-circle');
            $('#img_picture').css('visibility', 'visible').css('display','block');
            $.ajax({
                url: "/admission/picture?description="+description
            }).then(function(data) {
                if(data){
                    if(data.content_type.startsWith('image')){
                        $('#img_picture').attr('src','/admission'+data.file);
                    }else{
                        $('#img_picture').attr('src','');
                        $('#img_picture').css('visibility', 'hidden').css('display','none');
                    }
                }else{
                    $('#img_picture').css('visibility', 'hidden').css('display','none');
                }
            });
        }

        if(description == 'ID_CARD'){
            $('#btn_modify_id_document').attr('title', gettext('change_document'));
            $('#btn_modify_id_document').attr('class', 'btn btn-success pull-right');
            $('#spn_modify_id_document').attr('class', 'glyphicon glyphicon-ok-circle');
        }

        $('[id$="'+description+'"]').each(function(){
            if($(this).attr("id").startsWith('btn_load_assimilation_doc_')){
                $(this).attr('title', gettext('change_document'));
                $(this).attr('class', 'btn btn-success class_upload_assimilation');
                var spn_id = '#spn_' +$(this).attr("id");
                $(spn_id).attr('class', 'glyphicon glyphicon-ok-circle');
            }
            if( $(this).attr("id").startsWith('bt_load_doc_')){
                if($(this).attr("id")=='bt_load_doc_'+description  ){
                    $(this).attr('title', gettext('change_document'));
                    $(this).attr('class', 'btn btn-success');
                    var spn_id = '#spn_' +$(this).attr("id");
                    $(spn_id).attr('class', 'glyphicon glyphicon-ok-circle');
                }
            }
        });
    } else {
        if(description == 'ID_PICTURE'){
            $('#btn_modify_picture').attr('title', gettext('add_document'));
            $('#btn_modify_picture').attr('class', 'btn');
            $('#spn_modify_picture').attr('class', 'glyphicon glyphicon-upload');
            $('#img_picture').attr('src','');
            $('#img_picture').css('visibility', 'hidden').css('display','none');
        }

        if(description == 'ID_CARD'){
            $('#btn_modify_id_document').attr('title', gettext('add_document'));
            $('#btn_modify_id_document').attr('class', 'btn btn-default pull-right');
            $('#spn_modify_id_document').attr('class', 'glyphicon glyphicon-upload');
        }

        $('[id$="'+description+'"]').each(function() {
            if($(this).attr("id").startsWith('btn_load_assimilation_doc_') || $(this).attr("id").startsWith('bt_load_doc_')) {
                if($(this).attr("id")=='bt_load_doc_'+description || $(this).attr("id").startsWith('btn_load_assimilation_doc_')){
                    $(this).attr('title', gettext('add_document'));
                    $(this).attr('class', 'btn');
                    var spn_id = '#spn_' +$(this).attr("id");
                    $(spn_id).attr('class', 'glyphicon glyphicon-upload');
                }
            }
        });
    }
}

function validateEmail(sEmail) {
    var filter = /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
    if (filter.test(sEmail)) {
        return true;
    }else {
        return false;
    }
}

$("#bt_submit_profile").click(function() {
    $('#txt_message_error_profile').css('visibility', 'hidden').css('display','none');
    if (! valid(PROFILE_TAB)){
        return false;
    }
    return true;
});

$("#rd_previous_enrollment_false").click(function() {
    $('#txt_registration_id').val('');
    $('#txt_last_academic_year').val('');
});

function valid_profile_data(){
    // clear error messages
    $('#spn_number_children').html('');
    $('#spn_last_academic_year').html('');
    $('#spn_contact_adr_street').html('');
    $('#spn_contact_adr_number').html('');
    $('#spn_contact_adr_postal_code').html('');
    $('#spn_contact_adr_city').html('');
    $('#spn_contact_adr_country').html('');
    $('#spn_legal_adr_street').html('');
    $('#spn_legal_adr_number').html('');
    $('#spn_legal_adr_postal_code').html('');
    $('#spn_legal_adr_city').html('');
    $('#spn_legal_adr_country').html('');
    $('#spn_additional_email').html('');
    $('#spn_registration_id').html('');
    $('#spn_last_academic_year').html('');

    if($('#txt_number_children').val() != ''){
        if(! $.isNumeric( $('#txt_number_children').val())){
            $('#spn_number_children').text(gettext('number_invalid'));
            return false;
        }else{
            var nb_children = parseInt($('#txt_number_children').val());
            if(nb_children < 0 || nb_children >20){
                $('#spn_number_children').text(gettext('number_invalid'));
                return false;
            }
        }
    }
    if( $('#rd_previous_enrollment_true').prop('checked')){
        txt_registration_id
        if($('#txt_registration_id').val() == ''){
            $('#spn_registration_id').text(gettext('previous_enrollment_required_nb'));
            return false;
        }
        if($('#txt_last_academic_year').val() == ''){
            $('#spn_last_academic_year').text(gettext('previous_enrollment_required_year'));
            return false;
        }
    }
    if($('#txt_last_academic_year').val() != ''){
        if(! $.isNumeric( $('#txt_last_academic_year').val())){
            $('#spn_last_academic_year').text(gettext('number_invalid'));
            return false;
        }else{
            var year = parseInt($('#txt_last_academic_year').val());
            if(year < 1900 || year >3000){
                $('#spn_last_academic_year').text(gettext('number_invalid'));
                return false;
            }
        }
    }

    var legal_valid = true;
    if($('#txt_legal_adr_street').val() == '' ){
        $('#spn_legal_adr_street').text(gettext('legal_street'));
        legal_valid = false;
    }
    if($('#txt_legal_adr_number').val() == '' ){
        $('#spn_legal_adr_number').text(gettext('legal_number'));
        legal_valid = false;
    }
    if($('#txt_legal_adr_postal_code').val() == '' ){
        $('#spn_legal_adr_postal_code').text(gettext('legal_postal_code'));
        legal_valid = false;
    }
    if($('#txt_legal_adr_city').val() == '' ){
        $('#spn_legal_adr_city').text(gettext('legal_city'));
        legal_valid = false;
    }
    if($('#slt_legal_adr_country').prop('selectedIndex') <= 0 ){
        $('#spn_legal_adr_country').text(gettext('legal_country'));
        legal_valid = false;
    }

    if($('#rd_same_contact_legal_addr_false').prop("checked")){
        var contact_valid = true;
        if($('#txt_contact_adr_street').val() == '' ){
            $('#spn_contact_adr_street').text(gettext('contact_street'));
            contact_valid = false;
        }
        if($('#txt_contact_adr_number').val() == '' ){
            $('#spn_contact_adr_number').text(gettext('contact_number'));
            contact_valid = false;
        }
        if($('#txt_contact_adr_postal_code').val() == '' ){
            $('#spn_contact_adr_postal_code').text(gettext('contact_postal_code'));
            contact_valid = false;
        }
        if($('#txt_contact_adr_city').val() == '' ){
            $('#spn_contact_adr_city').text(gettext('contact_city'));
            contact_valid = false;
        }
        if($('#slt_contact_adr_country').prop('selectedIndex') <= 0 ){
            $('#spn_contact_adr_country').text(gettext('contact_country'));
            contact_valid = false;
        }
    }
    if(legal_valid == false || contact_valid == false){
        return false;
    }
    // email validation
    var sEmail = $('#txt_additional_email').val();
    if ($.trim(sEmail).length > 0 && validateEmail(sEmail) == false) {
        $('#spn_additional_email').text(gettext('invalid_email'));
        return false;
    }
    return true;
}

function valid_profile_navigation(){
    var message = new String("");
    if (($("#slt_nationality").prop('selectedIndex') <= 0
        || $("#slt_legal_adr_country").prop('selectedIndex') <= 0) || ($("#slt_nationality").val()=='-1' || $("#slt_legal_adr_country").val()=='-1')){
        message = gettext('msg_next_profil');
    }

    if($('#pnl_assimilation_criteria').is(":visible")){
        var cpt = 1;
        while(cpt <=7){
            if(! $("#assimilation_criteria_CRITERIA_"+ cpt+"_true").prop('checked') && ! $("#assimilation_criteria_CRITERIA_"+cpt+"_false").prop('checked') ){
                message += gettext('msg_assimilation_criteria');
                break;
            }
            cpt = cpt +1;
        }
    }

    if(message.trim().length > 0){
        $("#txt_message_error_profile_up").text(message);
        $('#txt_message_error_profile_up').css('visibility', 'visible').css('display','block');
        return false;
    }
    return true;
}

function change_menu(){
    var enableMyLink = true;
    var valid_localdegree = true;
    if($('#hdn_tab_active').val() < "2"){
        if ($('#hdn_coverage_access_degree').val()==''){
            valid_localdegree = false;
        }

        if($('#hdn_current_application_id').val()=='' || valid_localdegree == false){
            enableMyLink = false;
        }else{
            // verify some data
            if($("#slt_nationality").prop('selectedIndex')<=0 || $("#slt_legal_adr_country").prop('selectedIndex')<=0){
                enableMyLink = false;
            }
        }
    }
    if (enableMyLink) {
        $("#mn_diploma").removeClass("disabled").find("a").removeAttr("onclick");
        $("#mn_curriculum").removeClass("disabled").find("a").removeAttr("onclick");
        $("#mn_accounting").removeClass("disabled").find("a").removeAttr("onclick");
        $("#mn_sociological").removeClass("disabled").find("a").removeAttr("onclick");
        $("#mn_attachments").removeClass("disabled").find("a").removeAttr("onclick");
        $("#mn_submission").removeClass("disabled").find("a").removeAttr("onclick");
    } else {
        $("#mn_diploma").addClass("disabled").find("a").attr("onclick", "return false;");
        $("#mn_curriculum").addClass("disabled").find("a").attr("onclick", "return false;");
        $("#mn_accounting").addClass("disabled").find("a").attr("onclick", "return false;");
        $("#mn_sociological").addClass("disabled").find("a").attr("onclick", "return false;");
        $("#mn_attachments").addClass("disabled").find("a").attr("onclick", "return false;");
        $("#mn_submission").addClass("disabled").find("a").attr("onclick", "return false;");
    }
}

$("#slt_legal_adr_country").change(function() {
    change_menu();
});
$('#bt_submit_application').click(function() {
    change_menu();
    $('#demande_next_tab').val('1');
    return offer_steps(1);
});

$('[id^="bt_previous_diploma_step_"]').click(function() {
    change_menu();
    $('#hdn_tab_applications_status').val('True');
    set_following_tab(DEMAND_TAB);
    return true;
});

$('[id^="bt_next_diploma_step_"]').click(function() {
    change_menu();
    $('#hdn_tab_applications_status').val('True');
    set_following_tab(CURRICULUM_TAB);
    return true;
});

$('[id^="bt_previous_curriculum_step_"]').click(function() {
    change_menu();
    $('#hdn_tab_applications_status').val('True');
    set_following_tab(PREREQUISITES_TAB);
    return true;
});

$('[id^="bt_next_curriculum_step_"]').click(function() {
    change_menu();
    $('#hdn_tab_applications_status').val('True');
    set_following_tab(ACCOUNTING_TAB);
    return true;
});

$('[id^="bt_previous_sociological_step_"]').click(function() {
    change_menu();
    $('#hdn_tab_applications_status').val('True');
    set_following_tab(ACCOUNTING_TAB);
    return true;
});

$('[id^="bt_next_sociological_step_"]').click(function() {
    change_menu();
    $('#hdn_tab_applications_status').val('True');
    set_following_tab(ATTACHMENTS_TAB );
    return true;
});

$('[id^="bt_previous_accounting_step_"]').click(function() {
    change_menu();
    $('#hdn_tab_applications_status').val('True');
    set_following_tab(CURRICULUM_TAB);
    return true;
});

$('[id^="bt_next_accounting_step_"]').click(function() {
    change_menu();
    $('#hdn_tab_applications_status').val('True');
    set_following_tab(SOCIOLOGICAL_SURVEY_TAB );
    return true;
});

$('[id="chb_agree"]').click(function(event) {
    var target = $(event.target);
    var val = target.val();
    $('[id="bt_confirm_submission"]').prop( "disabled", true);
    if(target.prop("checked") && $('#hdn_application_valide').val()=="True"){
        $('[id="bt_confirm_submission"]').prop( "disabled", false);
    }
    return true;
});


$( document ).ready(function() {

  $.fn.jumper_select = function (options) {
    if (!$.fn.jumper_select.setup_done) {
      $.fn.jumper_select.setup();
    }
    var settings = $.extend({}, $.fn.jumper_select.defaults, options);

    return this.each(function () {
      var $select = $(this);
      var id = $select[0].id;

      $.fn.jumper_select.set("apply_action_" + id, settings.apply_action);

      var height = (settings.title == "" ? "50px" : "");
      var width = settings.width + "px";
      var html = `
  <div class="filter_field" id="filter_` + id + `" style='width:`+width+`;height:` + height + `;cursor:pointer' onclick="$.fn.jumper_select.create_filter_box('` + id + `')">
    <div class="title">` + settings.title + `</div>
    <div  
      class="text" 
      id="filters_` + id + `">Select</div>
` + $select[0].outerHTML + `
</div>
`;

      $select.replaceWith(html);

      $.fn.jumper_select.set("filter_field_name", id);
      $.fn.jumper_select.rebuild_filter_body();


    });
  };

  $.fn.jumper_select.defaults = {
    apply_action: function () {
      console.log("apply", this);
    },
    title: "default_title",
    width: 240
  };


  $.fn.jumper_select.setup = function () {
    $.fn.jumper_select.setup_done = true;
    $('head').append(`
<style>
  body, div, li, input, select, button { font-family: Poppins; margin:0; }

.filter_field { float:left; border:1px solid #ddd; border-radius:4px; height:60px; overflow:hidden; background-color:#f5f5f5;}
.filter_field .title { width:calc(100% - 20px); margin:8px 10px 0 10px; font-size:11px; }
.filter_field .text { width:calc(100% - 20px); margin:0px 10px; font-size:14px;  height:36px;cursor:pointer; line-height:36px;color:#666;}

select {height:34px; font-size:13px; padding: 0 10px 0 10px; }

#filter_box { width:240px; height:400px; display:none; position:absolute; border:1px solid #ccc; background-color:#f5f5f5; overflow:auto; }
#filter_box input { border:0;
      background-image: url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath d='M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z'/%3E%3Cpath d='M0 0h24v24H0z' fill='none'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-size: 18px 18px;
        background-position: 95% center; 
        width:218px; }
#filter_box_body { overflow:auto;height: 328px;background-color:#eee; cursor:pointer; overflow-x:hidden;}        
#filter_box_body div { cursor:pointer, width:100%;  padding:5px 10px; line-height:26px; font-size:12px; }
#filter_box_body div.selected { background-color:#eff; }
#filter_box_body div:hover { background-color:#ddd; }
.filter_search, .filter_search:focus { border:0; margin:0; padding:0; font-size:12px; }
#filter_box .clear_all {border-bottom:1px solid #ccc;text-align:right}
#filter_box .apply {text-align:center;width:80px;float:right;cursor:pointer; border-top:1px solid #ccc;height:36px;line-height:36px; text-align:right; font-size:12px; padding:0;}
#filter_box .clear { color:#ccc;text-align:center;width:80px;float:left;cursor:pointer; border-top:1px solid #ccc;height:36px;line-height:36px; text-align:left; font-size:12px; padding:0;}
#filter_box .clear span {margin-left:20px}
#filter_box .all { text-align:center;width:80px;float:left;cursor:pointer; border-top:1px solid #ccc;height:36px;line-height:36px; text-align:left; font-size:12px; padding:0;}
#filter_box .apply:hover  { background-color:#efe; }
#filter_box .clear:hover  { background-color:#fee; }
#filter_box .all:hover  { background-color:#eff; }
#filter_box input { height:35px; padding:0 10px; margin:2px;}
#filter_layer { opacity:0.5; cursor:pointer; display:none; width:100%; height:calc(100% - 0px); position:fixed; top:0px; left:0; z-index:99; background-color:white;}
</style>
  `);


    $.fn.jumper_select.values = {};
    $.fn.jumper_select.set = function (k, v) {
      $.fn.jumper_select.values[k] = v;
    };
    $.fn.jumper_select.get = function (k) {
      return ($.fn.jumper_select.values[k] || null);
    };
    var d = document.createElement("div");
    d.id = 'filter_box';
    document.body.appendChild(d);

    d = document.createElement("div");
    d.id = 'filter_layer';
    document.body.appendChild(d);
    $("#filter_layer").click(function () {
      $("#filter_layer").hide();
      $("#filter_box").hide();
    });
  };

  $.fn.jumper_select.create_filter_box = function (field_name) {
    var html = `<input style='margin:0' onkeyup='$.fn.jumper_select.rebuild_filter_body()' id='filter_search' placeholder='Search'>   
  <div id='filter_box_body'></div>

  <div onclick='$.fn.jumper_select.filter_all(true)' class='all'><div style="text-align:center">ALL</div></div>
  <div class='clear' onclick='$.fn.jumper_select.filter_all(false)'><span id='filter_clear_all'>CLEAR</span></div>
  <div onclick='$.fn.jumper_select.apply()' class='apply'><div style="text-align:center">APPLY</div></div>`;

    var offset = $("#filters_" + field_name).offset();
    $.fn.jumper_select.set("filter_field_name", field_name);

    $("#filter_box").css("z-index", 100).css("left", (offset.left) + "px").css("top", offset.top + "px").show().html(html);
    $("#filter_layer").show();
    $("#filter_search").focus();

    $.fn.jumper_select.rebuild_filter_body();
  };
  $.fn.jumper_select.rebuild_filter_body = function () {
    var filter_search = $("#filter_search").val() || "";
    var field_name = $.fn.jumper_select.get("filter_field_name");
    var filter_object = {
      selected: [],
      unselected: []
    };

    var options = document.getElementById(field_name).options;
    var opt, i, iLen;
    for (i = 0, iLen = options.length; i < iLen; i++) {
      opt = options[i];

      if (opt.selected) {
        filter_object.selected.push({
          value: opt.value,
          text: opt.text
        });
      }
      else {
        if (filter_search == '' || opt.text.toLowerCase().indexOf(filter_search.toLowerCase()) >= 0) {
          filter_object.unselected.push({
            value: opt.value,
            text: opt.text
          });
        }
      }
    }

    var filters_text = "";
    var html = "";
    var show_clear_all = false;
    for (i in filter_object.selected) {
      if (filter_object.selected.hasOwnProperty(i)) {
        opt = filter_object.selected[i];
        html += "<div onclick='$.fn.jumper_select.select_filter_option(`" + opt.value + "`, false)' class='selected'>" + opt.text + "</div>";
        filters_text += (filters_text == "" ? "" : ", ") + opt.text;
      }
    }
    if (filter_object.selected.length > 0) {
      show_clear_all = true;
    }
    for (i in filter_object.unselected) {
      if (filter_object.unselected.hasOwnProperty(i)) {
        opt = filter_object.unselected[i];
        html += "<div onclick='$.fn.jumper_select.select_filter_option(`" + opt.value + "`, true)'>" + opt.text + "</div>";
      }
    }
    $("#filter_box_body").html(html);
    $("#filter_clear_all").css("color", (show_clear_all ? '#000' : '#ccc'));
    if ($("#filter_" + field_name)[0].onchange && $("#filter_" + field_name)[0].onchange != "") {
      $("#filter_" + field_name)[0].onchange();
    }
    if (filters_text == "") {
      filters_text = "Select >";
    }
    $("#filters_" + field_name).html(filters_text);
  };
  $.fn.jumper_select.filter_all = function (sel) {
    var field_name = $.fn.jumper_select.get("filter_field_name");
    $('#' + field_name).children("option").prop("selected", sel);
    $.fn.jumper_select.rebuild_filter_body();
  };
  $.fn.jumper_select.select_filter_option = function (option, selected) {

    var field_name = $.fn.jumper_select.get("filter_field_name");
    var is_multiple = $('#' + field_name).prop('multiple');
    if(is_multiple) {
      var vals = $('#' + field_name).val() || [];
      if (!selected) {
        $.fn.jumper_select.remove(vals, option);
      }
      else {
        vals.push(option);
      }
      $('#' + field_name).val(vals);
    } else {
      var val = $('#' + field_name).val() || [];
      if (!selected) {
        val = null;
      } else {
        val=option
      }
      $('#' + field_name).val(val);
    }

    $.fn.jumper_select.rebuild_filter_body();
  };
  $.fn.jumper_select.remove = function (array, element) {
    const index = array.indexOf(element);
    array.splice(index, 1);
  };

  /*
  $.fn.jumper_select.draw_filter_field = function (field_name, field) {
    //   debugger;
    var options = field.data;
    var multiple = (field.multiple ? "multiple" : "");
    var html = "<div class='title'>" + field.title + "</div><div onclick='$.fn.jumper_select.create_filter_box(this.id.split(`filters_`)[1])' class='text' id='filters_" + field_name + "'>Select ></div>" + "<select style='display:none' onchange='$.fn.jumper_select.changed_filter(`" + field_name + "`)' " + multiple + " id='filter_" + field_name + "'>";
    var printed_list = {};
    for (var option in options) {
      if(options.hasOwnProperty(option)) {  
        var txt = options[option].name || options[option].id;
        if (!printed_list[options[option].id]) {
          printed_list[options[option].id] = true;
          html += "<option value='" + options[option].id + "'>" + txt + "</option>";
        }
      }
    }
    html += "</select>";
    $("#filter_field_" + field_name).html(html);
    $.fn.jumper_select.changed_filter(field_name);
//    w.sort_select("filter_" + field_name);
  };
*/
  $.fn.jumper_select.apply = function () {
    var field_name = $.fn.jumper_select.get("filter_field_name");

    $.fn.jumper_select.get("apply_action_" + field_name)();

    $("#filter_layer").hide();
    $("#filter_box").hide();
  };
});


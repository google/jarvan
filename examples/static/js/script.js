/*
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
*/
w.values = {};
w.appsList = ["module_a","module_b"];
w.appsLoaded = 0;

/** called by google auth */
check_login = function () { w.check_login(); };


/** execute logout */
w.sign_out = function() {
  $("#loading").hide();
  $("#main_container").hide();
  $("#signout").hide();
  //$("#please_sign_in").show();
  //$("#g-signin2").show();
  w.old_hash = localStorage.getItem("hash");
  localStorage.removeItem("token");
  localStorage.removeItem("hash");
  localStorage.removeItem("userName");
  $("#user_name").html("");

  var auth2 = gapi.auth2.getAuthInstance();
  auth2.signOut().then(function () {
    
    $.post( "/api/login/signout?hash="+w.old_hash, { },
      function(d){
        w.old_hash = null;
        document.location.href="/";
      });
    
  });
};


/** check if user is logged */
w.check_login=function() {
  try {
    var auth2 = gapi.auth2.getAuthInstance();
    var user = auth2.currentUser.get().getBasicProfile();

    if(typeof user=="object" && typeof user.getEmail()=="string") {
      $("#g-signin2").hide();
      $("#signout").show();

      var token = auth2.currentUser.get().getAuthResponse().id_token;

      if(localStorage.getItem("token")==token) {
        //w.run();
      } else {
        $.post( "/api/login/register_token?token="+token, { },
          function(d){
            if(d.user && d.user.name) {
              localStorage.setItem("token",token);
              localStorage.setItem("hash",d.user.hash);
              localStorage.setItem("userName",d.user.name);
              if(!w.already_run) {
                w.run();
              }
            } else {
              alert("Please use your @google.com account for authentication.\n\n")
              w.sign_out();
            }
          });
      }
    } else {
      $("#g-signin2").show();
      $("#signout").hide();
      $("#main_container").hide();
      $("#please_sign_in").show();
//      $("#header").show();
    }
  } catch(e) {
    $("#g-signin2").show();
    $("#signout").hide();
    $("#main_container").hide();
    $("#please_sign_in").show();
  }
};

/** show main screen */
w.run = function() {
  w.already_run = true;
  $("#header").show();

  w.hash=localStorage.getItem("hash");
  $("#user_name").html(localStorage.getItem("userName"));
  $("#g-signin2").hide();
  $("#signout").show();
  $("#please_sign_in").hide();
  $("#loading").hide();
  $("#main_container").show();

  w.load_js()    
   
};

//w.go = function(url) {
//  document.location.href = url;
//};

w.set_page_title = function(t) {
  $(".page_title").removeClass("selected");
  $("#page_title_"+t).addClass("selected");
}

/**
 * Loads a list of scripts sequencially in order
 *
 * @param jsList a list of scripts lo load from /s/js/apps
 * @param pos recursive position
*/
w.load_js = function() {
  w.appsLoaded=0;

  for(var i in w.appsList) {
    var appName = w.appsList[i];
    var script = document.createElement('script');
    script.src = "/static/js/" + appName + ".js?r="+Math.random();
    script.onload = function() { w.load_js2(); }
    document.head.appendChild(script);

  }
}

w.load_js2 = function() {
  w.appsLoaded++;

  if(w.appsLoaded == w.appsList.length) {
    for(var i in w.appsList) {
      var a = w.appsList[i];
      var p = w[a];
      w[a](p);
      w[a].set = w.set;
      w[a].get = w.get;
    }
    w.load_tables();
  }
}

w.set = function(k,v) { w.values[k] = v;}
w.get = function(k) { return (w.values[k] || null);}

w.setupApp = function (a) {
  console.log(a)
  w[a](w[a]);
}

w.strtoken = function(str,pos,token) {
  var a=str.split(token);
  var out = "";
  try {
    if(pos>0) {
      out = a[pos-1];
    } else if(pos<0) {
      out = a[a.length+pos];
    }
  } catch(e) {}
  if(typeof out == "undefined") {
    out = "";
  }
  return out;
}

w.go = function(p) {
  $("#logo-container").html("");
  
  if(typeof(p)=="undefined") {
    p = w.strtoken(document.location.pathname,2,"/");
  } 

  if(p!="" && w.appsList.indexOf(p)>=0 && w[p].run) {
    w[p].run();
  } else {
    w.projects.run();
  }

  //window.history.pushState({"html":"/"+p,"pageTitle":"/"+p},"", "/"+p);

  window.onresize = w.resize;
  w.resize();
}

w.load_tables = function() {
  w.go();
  return;
  
  w.get_json("/data/get_types",{}, function(d) {
    //localStorage.setItem("initData",JSON.stringify(d));
    if(d.email=="") {
      w.sign_out();
    }
    var types={};
    var countries = {};
    for(var i in d.types) {
      types[d.types[i].id] = d.types[i];
      countries[d.types[i].country]=1
    }
    w.set("types", types);
    w.set("countries", countries);

    w.go();
  });
}

w.get_json = function(url,data,success,error) {
  data = data || {};
  data["x-token"] = w.hash;
  error = error || (function(e) {
  data = e.responseJSON
    try {
      console.log('%c---- ERROR # '+data.error_id+' ----  '+data.file_txt,'color: red; font-weight: bold;');  
      console.log(data.message);
      console.log(data.sql);
      alert("error #"+data.error_id);
    } catch(f) {
      console.log("ERROR:", url, e,f)
    }
  });
  $.ajax({
    dataType: "json",
    url: "/api" + url,
    data: data,
    success: success,
    error: error
  });
}
w.post_json = function(url,data,success,error) {
  data = data || {};
  data["x-token"] = w.hash;
  error = error || (function(e) {
  data = e.responseJSON
    try {
      console.log('%c---- ERROR # '+data.error_id+' ----  '+data.file_txt,'color: red; font-weight: bold;');  
      console.log(data.message);
      console.log(data.sql);
      alert("error #"+data.error_id);
    } catch(f) {
      console.log("ERROR:", url, e,f)
    }
  });
  $.ajax({
    dataType: "json",
    method: "POST",
    url: "/api" + url,
    data: data,
    success: success,
    error: error
  });
}

w.resize = function(){
  var a = $("#filters").height() || 0;
  var c = $(window).height();

  $("#main_content").height(c - a - 65);
}

w.set_right_width = function(set_width) {

  w.right_width = w.right_width || 0; 
  $("#right_column_title").hide();
  if(set_width==100) {
    w.right_width = 100;
    $("#right_expand").hide();
    $("#right_hide").show();
    $("#right_column").show();
    $("#right_column_title").show();
  } else {
    if(w.right_width==100) {
      w.right_width = 50;
      $("#right_expand").show();
      $("#right_hide").show();
      $("#right_column").show();
    } else {
      w.right_width = 0;
      window.setTimeout(function() { $("#right_column").hide(); },100);
    }
  }
  $("#right_column").css("width",w.right_width+"%");
}

w.uc_words = function( str )
{
    var pieces = str.split(" ");
    for ( var i = 0; i < pieces.length; i++ )
    {
        var j = pieces[i].charAt(0).toUpperCase();
        pieces[i] = j + pieces[i].substr(1).toLowerCase();
    }
    return pieces.join(" ");
}

w.toast = function(t) {
  $("#toast").html(t).addClass("show");
  setTimeout(function(){ $("#toast").removeClass("show") }, 3000);
}

w.get_param = function(p) {
  var url_string = window.location.href
  var url = new URL(url_string);
  return (url.searchParams.get(p) || "");
}

w.to_image = function(div) {
  for(var i=0;i<=10;i++) {
    div = div.parentElement;
    if(div.classList.contains("to_image")){
      html2canvas(div).then(canvas => { $(div).html(canvas); });
      break;      
    }
  }
  console.log(div.parentElement);
}


w.sort_tables = function() {
  $( "table.sortable" ).each(function( index ) {
    var tds = this.getElementsByTagName("thead")[0].getElementsByTagName("tr")[0].getElementsByTagName("td");
    for(var i=0; i<tds.length; i++) {
       tds[i].setAttribute('onclick', 'w.sort_row(this,'+i+')');
    }
  });
}

w.sort_row = function(ptable, n) {
  table = ptable.parentElement.parentElement;
  if(table.tagName.toLowerCase()=="thead") {
    table = table.parentElement;
  }

  w.lastOrder = "DESC"; 
  if(table.rows[0].cells[n].dataset.order) {
    w.lastOrder = table.rows[0].cells[n].dataset.order;
  }
  if(w.lastOrder=="DESC") {
    w.lastOrder="ASC";
  } else {
    w.lastOrder="DESC";
  }
  table.rows[0].cells[n].dataset.order=w.lastOrder;

  var l=table.rows.length;
  var rows=[];
  for(var i=1;i<l;i++){
    rows.push(table.rows[1]);
    table.deleteRow(1);
  }
  rows.sort(function(first, second) {
    var x = first.cells[n].innerHTML;
    var y = second.cells[n].innerHTML;
      if(x.replace(/[\ |\$]/g,'')*1==x.replace(/[\ |\$]/g,'') && y.replace(/[\ |\$]/g,'')*1==y.replace(/[\ |\$]/g,'')) {
        x=x.replace(/[\ |\$]/g,'')*1;
        y=y.replace(/[\ |\$]/g,'')*1;
      } else {
        x=x.toLowerCase();
        y=y.toLowerCase();
      }
    if(w.lastOrder=="ASC") {
      return (x<y? -1: 1);
    } else {
      return (y>x? 1: -1);
    }
  });
  for(var i=0;i<l-1;i++){
    table.appendChild(rows[i]);
  }
}

if(localStorage.getItem("hash")) {
  w.run();
} else {
  check_login();
}

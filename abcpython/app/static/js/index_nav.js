/****针对winphone修改****/
if (navigator.userAgent.match(/IEMobile\/10\.0/)) {
  var msViewportStyle = document.createElement("style")
  msViewportStyle.appendChild(
    document.createTextNode(
      "@-ms-viewport{width:auto!important}"
    )
  )
  document.getElementsByTagName("head")[0].appendChild(msViewportStyle)
}
/**********字符串去除空格操作**********/
//前后都去除空格
String.prototype.Trim = function() {
  return this.replace(/(^\s*)|(\s*$)/g, "");
}
//去除左边空格
String.prototype.LTrim = function() {
  return this.replace(/(^\s*)/g, "");
}
//去除右边空格
String.prototype.RTrim = function() {
  return this.replace(/(\s*$)/g, "");
}
//显示悬浮菜单
var leftnav = {
  level: 1,
  isrunning: false,
  togglenav: function() {
    if (leftnav.isrunning) {
      return false;
    }
    leftnav.isrunning = true;
    switch (leftnav.level) {
      case 1:
        $(".navfloat").animate({
          left: "300px"
        }, 400);
        $(".navbody").animate({
            width: "80px"
          },
          400, function() {
            leftnav.isrunning = false;
            leftnav.level = 2;
            $(".navtitle span.icon").removeClass("icon-double-angle-right");
            $(".navtitle span.icon").addClass('icon-double-angle-left');
            $(".navbody .navitems span.nav-text").show();
          });
        break;
      case 2:
        $(".navbody .navitems span.nav-text").hide();
        $(".navfloat").animate({
          left: "40px"
        }, 400);
        $(".navfloat").fadeOut(400);
        $(".navbody").animate({
            width: "33px"
          },
          400, function() {
            leftnav.isrunning = false;
            leftnav.level = 1;
            $(".navtitle span.icon").addClass("icon-double-angle-right");
            $(".navtitle span.icon").removeClass('icon-double-angle-left');
          });
        break;
      default:
        leftnav.isrunning = false;
        break;
    }
  },
  shownav: function() {
    if (leftnav.isrunning && leftnav.level != 1) {
      return false;
    }
    leftnav.isrunning = true;
    $(".navfloat").animate({
      left: "87px"
    }, 400);
    $(".navbody").animate({
        width: "80px"
      },
      400, function() {
        leftnav.isrunning = false;
        leftnav.level = 2;
        $(".navtitle span.icon").removeClass("icon-double-angle-right");
        $(".navtitle span.icon").addClass('icon-double-angle-right');
        $(".navbody .navitems span.nav-text").show();
      });
  },
  hidenav: function() {
    if (leftnav.isrunning && leftnav.level != 2) {
      return false;
    }
    leftnav.isrunning = true;
    $(".navbody .navitems span.nav-text").hide();
    $(".navfloat").animate({
      left: "40px"
    }, 400);
    $(".navfloat").fadeOut(400);
    $(".navbody").animate({
        width: "33px"
      },
      400, function() {
        leftnav.isrunning = false;
        leftnav.level = 1;
        $(".navtitle span.icon").addClass("icon-double-angle-right");
        $(".navtitle span.icon").removeClass('icon-double-angle-left');
      });
  },
  togglefloat: function() {
    $(".navfloat").toggle(400);
  }
}

function shownavs() {
  leftnav.togglenav();
}

function showfloat() {
  leftnav.togglefloat();
}
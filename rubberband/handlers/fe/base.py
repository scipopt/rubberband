from collections import Iterable
from datetime import datetime
from tornado.web import RequestHandler
from tornado.options import options
import traceback

from rubberband.constants import NONE_DISPLAY, INFINITY_KEYS, INFINITY_MASK, FORMAT_DATETIME_SHORT


class BaseHandler(RequestHandler):
    '''
    Custom overrides.
    '''
    def get_current_user(self):
        if not self.settings["debug"]:
            # self.request is single HTTP requestobject of type 'tornado.httputil.HTTPServerRequest'
            headers = dict(self.request.headers.get_all())
            return headers.get("X-Forwarded-Email")
        else:
            return "debug"

    def get_cookie(self, name="_oauth2_proxy"):
        if not self.settings["debug"]:
            cookie_val = self.request.cookies.get(name).value
            return cookie_val
        else:
            return None

    def write_error(self, status_code, msg="", **kwargs):
        if status_code == 400:
            self.render("400.html", msg=msg)
            return
        if status_code == 404:
            #  'Simply render the template to a string and pass it to self.write'
            self.render("404.html")
            return
        else:
            msg = "\n".join(traceback.format_exception(*kwargs["exc_info"]))
            self.render("500.html", msg=msg)
            return

    def get_template_namespace(self):
        """Returns a dictionary to be used as the default template namespace.

        May be overridden by subclasses to add or modify values.

        The results of this method will be combined with additional
        defaults in the `tornado.template` module and keyword arguments
        to `render` or `render_string`.
        """
        namespace = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            _=self.locale.translate,
            pgettext=self.locale.pgettext,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.reverse_url,
            format_attr=self.format_attr,
            format_attrs=self.format_attrs,
            get_objsen=self.get_objsen,
            are_equivalent=self.are_equivalent,
            options=options,
        )

        # additional ui modules
        namespace.update(self.ui)

        return namespace

    def format_attr(self, obj, attr):
        '''
        Format (null) values (attributes attr of obj).
        Value gets properly formatted if attr is a single attribute.
        If attr is a list, the keys are concatenated with " ".

        attr: key or list of keys
        '''
        if isinstance(attr, list):
            value = []
            for i in attr:
                v = getattr(obj, i, None)
                if v is not None and v != "":
                    value.append(v)
            if value == []:
                return NONE_DISPLAY
            return " ".join(value)
        else:
            value = getattr(obj, attr, None)
            if value not in (None, ""):
                if attr in INFINITY_KEYS and value == INFINITY_MASK:
                    return float("inf")
                if attr.endswith("_timestamp") or attr.endswith("expirationdate"):
                    return datetime.strftime(value, FORMAT_DATETIME_SHORT)
                if isinstance(value, str):
                    return value
                if isinstance(value, Iterable):
                    return ", ".join([str(v) for v in value])
                return value
            return NONE_DISPLAY

    def get_objsen(self, objs, inst_name):
        '''
        Return the objective sense based on the fields Objsense, PrimalBound, DualBound
        maximize: -1 (pb <= db)
        minimize: 1  (pb >= db)

        objs: set/list of TestSets
        inst_name: instance/problem name
        '''
        objsen = None
        for o in objs:
            objsen = getattr(o.children[inst_name], "Objsense", None)
            if objsen is not None:
                return float(objsen)
        for o in objs:
            try:
                pb = float(getattr(o.children[inst_name], "PrimalBound", None))
                db = float(getattr(o.children[inst_name], "DualBound", None))
                if pb > db:
                    # minimize
                    return 1
                elif pb < db:
                    # maximize
                    return -1
            except:
                pass
        return 0

    def format_attrs(self, objs, attr, inst_name):
        '''
        Return sorted attribute (attr) of an instance (inst_name)
        from multiple TestSets (objs) as a formatted string separated by newlines.

        objs: set/list of TestSets
        attr: attribute
        inst_name: instance/problem name
        '''
        attr_str = []
        for o in objs:
            attr_str.append(getattr(o.children[inst_name], attr, None))

        partial_list = sorted([a for a in attr_str if a is not None], reverse=True)
        partial_list.extend([NONE_DISPLAY for a in attr_str if a is None])
        return "\n".join(map(str, partial_list))

    def are_equivalent(self, one, two, attr):
        '''
        Decide if the data in attr is the same in both TestSets one and two.
        '''
        a = self.format_attr(one, attr)
        b = self.format_attr(two, attr)
        return a == b

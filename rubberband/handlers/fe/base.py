"""Common class to derive all rubberband web request handlers from."""
from collections.abc import Iterable
from datetime import datetime
from tornado.web import RequestHandler
from tornado.options import options
from rubberband.utils.gitlab import get_user_access_level, get_username
import traceback

from rubberband.models import TestSet
from rubberband.constants import NONE_DISPLAY, INFINITY_KEYS, \
        INFINITY_MASK, INFINITY_DISPLAY, FORMAT_DATETIME_LONG
from rubberband.utils.helpers import shorten_str, get_link, shortening_span, \
        shortening_repres_id, rb_join_arg


class BaseHandler(RequestHandler):
    """Custom overrides."""

    # default datatable style
    rb_dt_compact = "compact"
    rb_dt_borderless = ""
    rb_dt_bordered = ""
    rb_dt_table = ""

    def prepare(self):
        """Called at the beginning of a request before get/post/and so on."""
        self.current_user = self.get_current_user()
        if self.access_level < 10:
            self.write_error(status=403, msg="Sorry, you don't have permission to view this page.")

    def has_permission(self, testrun=None, action="read"):
        """Decide whether user is permitted to interact with testrun."""
        if self.settings["debug"]:
            return True

        usr = get_username(self.current_user).lower()
        if testrun is not None:
            if action == "delete":
                return (usr == testrun.uploader.lower() or self.access_level == 50)
            elif action == "edit":
                return (usr == testrun.uploader.lower() or self.access_level > 25)
            elif action == "read":
                return (usr == testrun.uploader.lower() or self.access_level > 5)
        else:
            if action == "delete":
                return self.access_level == 50
            elif action == "edit":
                return self.access_level > 25
            elif action == "read":
                return self.access_level > 5

    def get_rb_base_url(self):
        """
        Url where the rubberband instance lives.

        Returns
        -------
        str
            the rubberband url
        """
        return self.request.protocol + "://" + self.request.host

    def get_rb_url(self):
        """
        Url where the rubberband instance lives.

        Returns
        -------
        str
            the rubberband url
        """
        return self.get_rb_base_url() + self.request.uri

    def get_current_user(self):
        """
        Get the name of the User that sent the request.

        Returns
        -------
        str
            Current user
        """
        if not self.settings["debug"]:
            # self.request is single HTTP requestobject of type 'tornado.httputil.HTTPServerRequest'
            headers = dict(self.request.headers.get_all())
            email = headers.get("X-Forwarded-Email")
            self.access_level = get_user_access_level(email)
            return email
        else:
            self.access_level = 50
            return "debug"

    def get_cookie(self, name="_oauth2_proxy", default=None):
        """
        Get the cookie from the request.

        Parameters
        ----------
        name : str
            The name of the cookie

        Returns
        -------
        str
            The value of the cookie.
        """
        if self.settings["debug"] and name == "_oauth2_proxy":
            return None
        else:
            cookie = self.cookies.get(name)
            if cookie is not None:
                return cookie.value
            else:
                return default

    def clear_all_cookies(self):
        """Clear all cookies that are defined."""
        for i in self.cookies:
            self.clear_cookie(i)

    def get_all_cookies(self):
        """Get all cookies that are defined as a dictionary."""
        mycookies = {}
        for i in self.cookies:
            val = self.get_cookie(i)
            if val == "":
                self.clear_cookie(i)
            else:
                mycookies[i] = val
        return mycookies

    def write_error(self, status_code=400, **kwargs):
        """
        Send an error page back to the user.

        This needs to be overwritten for error handling,
        as it gets called when a handler raises an HTTPError.

        Parameters
        ----------
        status_code : int
            The status code of the error to be written.
        kwargs : keyword arguments
            keyword arguments for `traceback.format_exception`
        """
        reason = kwargs.get('reason', "Error")

        log_message = ""
        if ("msg" in kwargs):
            log_message = kwargs["msg"]
        if ("exc_info" in kwargs):
            log_message = "\n".join(traceback.format_exception(*kwargs["exc_info"]))

        if status_code == 204:
            reason = "No content"
        elif status_code == 400:
            reason = "Bad Request"
        elif status_code == 403:
            reason = "Forbidden"
        elif status_code == 404:
            reason = "Not Found"
        elif status_code == 500:
            reason = "Internal Server Error"

        self.render("error.html", status_code=status_code, page_title=reason, msg=log_message)

    def get_template_namespace(self):
        """Return a dictionary to be used as the default template namespace.

        May be overridden by subclasses to add or modify values.

        The results of this method will be combined with additional
        defaults in the `tornado.template` module and keyword arguments
        to `render` or `render_string`.

        Define default values for templates.
        """
        namespace = super(BaseHandler, self).get_template_namespace()

        name_space = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            has_permission=self.has_permission,
            locale=self.locale,
            _=self.locale.translate,
            pgettext=self.locale.pgettext,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.reverse_url,
            clusterbench=self.clusterbench,
            format_attr=self.format_attr,
            format_type=self.format_type,
            format_attrs=self.format_attrs,
            get_objsen=self.get_objsen,
            are_equivalent=self.are_equivalent,
            shorten_str=shorten_str,
            shortening_span=shortening_span,
            shortening_repres_id=shortening_repres_id,
            rb_join_arg=rb_join_arg,
            get_link=get_link,
            options=options,

            page_title=None,
            status_code='404',  # error code
            checkboxes=False,
            radiobuttons=False,
            tablename='results-table',
            modalheading=None,
            modalbody=None,
            modalfooter=None,
            representation=None,
            ipet_long_table=None,
            ipet_aggregated_table=None,
            get_empty_header=False,

            rb_dt_compact=self.rb_dt_compact,
            rb_dt_borderless=self.rb_dt_borderless,
            rb_dt_bordered=self.rb_dt_bordered,
            rb_dt_table=self.rb_dt_table,
        )

        # additional ui modules
        namespace.update(self.ui)
        namespace.update(name_space)

        return namespace

    def format_type(self, obj, attr):
        """
        Return type of attribute of obj.

        Parameters
        ----------
        obj : object
        attr : attribute of obj

        Returns
        -------
        str
            type of attr of obj or ""
        """
        if attr in ["instance_type"]:
            return "text"
        if attr in ["OriginalProblem_Vars", "OriginalProblem_InitialNCons",
                "PresolvedProblem_InitialNCons", "PresolvedProblem_Vars", "DualBound",
                "PrimalBound", "Gap", "Iterations", "Nodes", "TotalTime_solving"]:
            return "number"
        value = getattr(obj, attr, None)
        if isinstance(value, str):
            return "text"
        if isinstance(value, float) or isinstance(value, int):
            return "number"
        return ""

    def clusterbench(self, obj):
        """Format ClusterBenchmarkID to a date."""
        cbid = self.format_attr(obj.metadata, "ClusterBenchmarkID")
        return "({}.{}.{})".format(cbid[6:8], cbid[4:6], cbid[0:4])

    def format_attr(self, obj, attr):
        """
        Format values (attributes attr of obj).

        Value gets properly formatted if attr is a single attribute.
        If attr is a list, the keys are concatenated with " ".

        Parameters
        ----------
        obj : object
        attr: key or list of keys of obj

        Returns
        -------
        str
            type of attr of obj
        """
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
            # treat time_mod differently
            if attr == "time_mod":
                val_tlim = getattr(obj, "time_limit", None)
                val_tfac = getattr(obj, "time_factor", None)
                if val_tfac is not None:
                    return "x {}".format(val_tfac)
                elif val_tlim is not None:
                    return "{}s".format(val_tlim)
                else:
                    return ""

            # get value
            value = getattr(obj, attr, None)
            if value not in (None, ""):
                if attr == "conflict/uselocalrows":
                    return (value == 0)
                if attr in INFINITY_KEYS and value == INFINITY_MASK:
                    return INFINITY_DISPLAY
                if (type(value) is int or type(value) is float):
                    return value
                if attr in ["DualBound", "PrimalBound"]:
                    return "%.4f" % value
                if attr in ["SolvingTime", "TotalTime_solving", "Gap"]:
                    return "%.2f" % value
                if attr in ["Iterations"]:
                    return int(value)
                if attr.endswith("_timestamp") or attr.endswith("expirationdate"):
                    return datetime.strftime(value, FORMAT_DATETIME_LONG)
                if isinstance(value, str):
                    return value
                if isinstance(value, Iterable):
                    return ", ".join([str(v) for v in value])
                return value
            return NONE_DISPLAY

    def get_objsen(self, objs, inst_name):
        """
        Return the objective sense based on the fields Objsense, PrimalBound, DualBound.

        Parameters
        ----------
        objs: set/list of TestSets
        inst_name: instance/problem name

        Returns
        -------
        int
            -1 if obj is a maximation problem (pb <= db), 1 if minimization (pb >= db), 0 else
        """
        objsen = None
        for o in objs:
            objsen = getattr(o.results[inst_name], "Objsense", None)
            if objsen is not None:
                return float(objsen)
        for o in objs:
            try:
                pb = float(getattr(o.results[inst_name], "PrimalBound", None))
                db = float(getattr(o.results[inst_name], "DualBound", None))
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
        """
        Return sorted attribute (attr) of an instance (inst_name) from multiple TestSets (objs).

        Parameters
        ----------
        objs: set/list of TestSets
        attr: attribute
        inst_name: instance/problem name

        Returns
        -------
        str
            a formatted string separated by newlines.
        """
        attr_str = []
        for o in objs:
            val = self.format_attr(o.results[inst_name], attr)
            attr_str.append(val)

        partial_list = sorted([a for a in attr_str
            if a is not None and type(a) in [int, float]], reverse=True)
        partial_list.extend(sorted([a for a in attr_str
            if a is not None and type(a) not in [int, float]], reverse=True))
        partial_list.extend([NONE_DISPLAY for a in attr_str if a is None])
        return "\n".join(map(str, partial_list))

    def are_equivalent(self, sets, attr):
        """
        Decide if the data in attr is the same in all TestSets.

        Skip values that don't exist.

        Parameters
        ----------
        sets : list of TestSets
        attr : attribute

        Returns
        -------
        bool
        """
        if len(sets) <= 1:
            return False

        if attr == "number_instances":
            length = [len(ts.results.to_dict().keys()) for ts in sets]
            old = length[0]
            for i in length:
                new = i
                if old != new:
                    return False
            return True

        vals = [getattr(ts, attr, None) for ts in sets]
        nonzeros = [val for val in vals if val is not None]
        try:
            unique_nonzeros = set(nonzeros)  # this does not work for lists
        except TypeError:
            nonzeros = [','.join(val) for val in vals if val is not None]
            unique_nonzeros = set(nonzeros)

        return (len(unique_nonzeros) <= 1)

    def get_starred_testruns(self):
        """Get a list of the testruns that are starred by the user."""
        starred_string = self.get_cookie("starred-testruns", None)

        starred = []
        if starred_string:
            starred = starred_string.split(",")

        starred = set(starred)

        testruns = []
        for i in starred:
            try:
                testruns.append(TestSet.get(id=i))
            except:
                pass
        return testruns

    def get_testrun_table(self, testruns, tablename, checkboxes=True, get_empty_header=False):
        """Get a table of testruns."""
        table = None
        if testruns != [] or get_empty_header:
            table = self.render_string("results_table.html", results=testruns,
                    tablename=tablename, checkboxes=checkboxes, get_empty_header=get_empty_header)
        return table

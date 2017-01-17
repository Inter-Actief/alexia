from json import dumps

from django.http import HttpResponse
from django.urls import reverse
from django.views.generic.base import TemplateView
from jsonrpc import mochikit
from jsonrpc.site import jsonrpc_site


class APIBrowserView(TemplateView):
    template_name = 'browse.html'
    site = jsonrpc_site
    mountpoint = 'jsonrpc_mountpoint'

    def get(self, request, *args, **kwargs):
        # Override get to provide mochikit.js and interpreter.js
        if request.GET.get('f', None) == 'mochikit.js':
            return HttpResponse(mochikit.mochikit, content_type='application/x-javascript')
        if request.GET.get('f', None) == 'interpreter.js':
            return HttpResponse(mochikit.interpreter, content_type='application/x-javascript')

        return super(APIBrowserView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(APIBrowserView, self).get_context_data(**kwargs)

        desc = self.site.service_desc()
        methods = sorted(desc['procs'], key=lambda x: x['name'])

        context['methods'] = methods
        context['method_names_str'] = dumps([m['name'] for m in desc['procs']])
        context['mountpoint'] = reverse(self.mountpoint)

        return context


class APIDocumentationView(TemplateView):
    template_name = 'api/documentation.html'
    site = jsonrpc_site
    mountpoint = 'jsonrpc_mountpoint'
    methods = None

    def get_context_data(self, **kwargs):
        context = super(APIDocumentationView, self).get_context_data(**kwargs)

        desc = self.site.service_desc()
        methods = sorted(desc['procs'], key=lambda x: x['name'])

        # Filter methods if filter is provided
        if self.methods is not None:
            methods = [method for method in methods if method['name'] in self.methods]

        # Strip leading spaces if first line starts with spaces
        for method in methods:
            summarylines = method['summary'].splitlines()

            # Strip first line if emtpy
            if not summarylines[0].strip():
                del summarylines[0]

            # Strip last line if emtpy
            if not summarylines[-1].strip():
                del summarylines[-1]

            if summarylines[0].startswith('    '):
                result = []
                for line in summarylines:
                    if line.startswith('    '):
                        result.append(line[4:])
                    else:
                        result.append(line)
                method['summary'] = '\n'.join(result)

        context['methods'] = methods
        context['mountpoint'] = reverse(self.mountpoint)

        return context


class APIv1DocumentationView(APIDocumentationView):
    template_name = 'api/documentation_v1.html'
    methods = ['authorization.add', 'authorization.end', 'authorization.list', 'login', 'logout', 'order.get',
               'order.marksynchronized', 'order.unsynchronized', 'organization.current.get',
               'organization.current.set', 'rfid.add', 'rfid.list', 'rfid.remove', 'user.add',
               'user.exists', 'user.get']

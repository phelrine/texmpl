#!/usr/bin/env python
from optparse import OptionParser
import os
from os import path
import subprocess
import getpass
import shutil

texmplate_dir = path.dirname(path.abspath(__file__))
template_dir = path.join(texmplate_dir, 'template')

class ProjectGenerator(object):
    def generate(self):
        self.make_project_dir()
        if self.opts.compile:
            self.compile_tex()

    def make_project_dir(self):
        pass

    def compile_tex(self):
        pass


class DefaultProjectGenerator(ProjectGenerator):
    def __init__(self, opts):
        self.opts = opts
        self.project_dir = path.join(os.getcwd(), self.opts.project)
        self.tex_file = path.join(self.project_dir, "document.tex")


    def make_project_dir(self):
        if path.exists(self.project_dir):
            raise Exception, '%s already exists.' % self.project_dir
        else:
            os.mkdir(self.project_dir)

        template_file = path.join(template_dir, 'template.tex.tmpl' if self.opts.bibtex else 'template-nobibtex.tex.tmpl')
        with open(template_file) as f:
            doc = f.read() % {'title': self.opts.project, #TODO: escape special chars
                              'author': getpass.getuser()}

        with open(self.tex_file, 'w') as f:
            f.write(doc)

        shutil.copy(path.join(template_dir, 'references.bib.tmpl'), path.join(self.project_dir, 'references.bib'))


    def compile_tex(self):
        filename, ext = path.splitext(self.tex_file)
        os.chdir(self.project_dir)

        subprocess.call(['platex', filename])
        subprocess.call(['dvipdfmx', filename])

        os.chdir(os.getcwd())


class OmakeProjectGenerator(ProjectGenerator):
    def __init__(self, generator):
        self.generator = generator
        self.opts = generator.opts
        self.project_dir = generator.project_dir


    def make_project_dir(self):
        self.generator.make_project_dir()
        shutil.copy(path.join(template_dir, 'OMakeroot.tmpl'), path.join(self.project_dir, 'OMakeroot'))

        with open(path.join(template_dir, 'OMakefile.tmpl')) as tmpl:
            with open(path.join(self.project_dir, 'OMakefile'), 'w') as dst:
                dst.write(tmpl.read() % {'filename': 'document'})


    def compile_tex(self):
        os.chdir(self.project_dir)
        subprocess.call(['omake'])
        os.chdir(os.getcwd())


if __name__ == '__main__':
    parser = OptionParser('')
    parser.add_option('-p', '--project', dest = 'project', help = 'project name')
    parser.add_option('-d', '--dest', dest = 'dst', help = 'project path')
    parser.add_option('--omake', dest = 'omake', action = 'store_true', default = False)
    parser.add_option('--no-bibtex', dest = 'bibtex', action = 'store_false', default = True)
    parser.add_option('--no-compile', dest = 'compile', action = 'store_false', default = True)
    opts, args = parser.parse_args()
    if not opts.project:
        assert len(args) > 0
        opts.project = args[0]

    generator = DefaultProjectGenerator(opts)
    if opts.omake:
        generator = OmakeProjectGenerator(generator)

    generator.generate()

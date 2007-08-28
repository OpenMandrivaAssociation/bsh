# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define section		free

Name:           bsh
Version:        1.3.0
Release:        %mkrel 9.1.1
Epoch:		0
Summary:        Lightweight Scripting for Java
License:        LGPL
Source0:        %{name}-%{version}-src.tar.bz2
Patch0:		%{name}-build.patch
Patch1:		%{name}-readline.patch
BuildRequires:  ant, ant-trax, bsf, perl
Requires:	bsf
Requires:	jpackage-utils >= 0:1.6
#BuildRequires:  libreadline-java
Url:            http://www.beanshell.org/
Group:          Development/Java
%if ! %{gcj_support}
Buildarch:      noarch
%endif
Buildroot:      %{_tmppath}/%{name}-%{version}-buildroot

%if %{gcj_support}
BuildRequires:		java-gcj-compat-devel
Requires(post):		java-gcj-compat
Requires(postun):	java-gcj-compat
%endif

%description
BeanShell is a small, free, embeddable, Java source interpreter with
object scripting language features, written in Java. BeanShell executes
standard Java statements and expressions, in addition to obvious
scripting commands and syntax. BeanShell supports scripted objects as
simple method closures like those in Perl and JavaScript(tm).
You can use BeanShell interactively for Java experimentation and
debugging or as a simple scripting engine for your applications. In
short: BeanShell is a dynamically interpreted Java, plus some useful
stuff. Another way to describe it is to say that in many ways BeanShell
is to Java as Tcl/Tk is to C: BeanShell is embeddable - You can call
BeanShell from your Java applications to execute Java code dynamically
at run-time or to provide scripting extensibility for your applications.
Alternatively, you can call your Java applications and objects from
BeanShell; working with Java objects and APIs dynamically. Since
BeanShell is written in Java and runs in the same space as your
application, you can freely pass references to "real live" objects into
scripts and return them as results.

%package manual
Summary:        Manual for %{name}
Group:          Development/Java

%description manual
Documentation for %{name}.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java
Requires(post):   /bin/rm,/bin/ln
Requires(postun): /bin/rm

%description javadoc
Javadoc for %{name}.

%package demo
Summary:        Demo for %{name}
Group:          Development/Java
AutoReqProv:	no
Requires:       %{name} = %{epoch}:%{version}-%{release}
Requires:	/usr/bin/env

%description demo
Demonstrations and samples for %{name}.

%prep
%setup -q -n BeanShell
%patch0 -p1
#%patch1 -p1
find . -name "*.jar" -exec rm -f {} \;
# remove all CVS files
for dir in `find . -type d -name CVS`; do rm -rf $dir; done
for file in `find . -type f -name .cvsignore`; do rm -rf $file; done

%build
mkdir -p lib
#export CLASSPATH=$(build-classpath bsf libreadline-java)
export CLASSPATH=$(build-classpath bsf)
export OPT_JAR_LIST=
# remove servlet dependency
rm -rf src/bsh/servlet
%ant -Dexclude-servlet='bsh/servlet/*' compile
%ant -Dexclude-servlet='bsh/servlet/*' jarall
%ant -Dexclude-servlet='bsh/servlet/*' javadoc
%ant -Dexclude-servlet='bsh/servlet/*' bshdoc
(cd docs/faq && %ant)
(cd docs/manual && %ant)

%install
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -m 644 dist/%{name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} ${jar/-%{version}/}; done)
# manual
find docs -name ".cvswrappers" -exec rm -f {} \;
find docs -name "*.xml" -exec rm -f {} \;
find docs -name "*.xsl" -exec rm -f {} \;
find docs -name "*.log" -exec rm -f {} \;
(cd docs/manual && mv html/* .)
(cd docs/manual && rm -rf html)
(cd docs/manual && rm -rf xsl)
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
# demo
for i in `find tests -name \*.bsh`; do
  perl -p -i -e 's,^\n?#!(/(usr/)?bin/java bsh\.Interpreter|/bin/sh),#!/usr/bin/env %{_bindir}/%{name},' $i
  if head -1 $i | grep '#!/usr/bin/env %{_bindir}/%{name}' >/dev/null; then
    chmod 755 $i
  fi
done
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -pr tests $RPM_BUILD_ROOT%{_datadir}/%{name}
# scripts
install -d $RPM_BUILD_ROOT%{_bindir}

cat > $RPM_BUILD_ROOT%{_bindir}/%{name} << EOF
#!/bin/sh
#
# %{name} script
# JPackage Project (http://jpackage.sourceforge.net)

# Source functions library
. %{_datadir}/java-utils/java-functions

# Source system prefs
if [ -f %{_sysconfdir}/%{name}.conf ] ; then
  . %{_sysconfdir}/%{name}.conf
fi

# Source user prefs
if [ -f \$HOME/.%{name}rc ] ; then
  . \$HOME/.%{name}rc
fi

# Configuration
MAIN_CLASS=bsh.Interpreter
if [ -n "\$BSH_DEBUG" ]; then
  BASE_FLAGS=-Ddebug=true
fi

BASE_JARS="%{name}.jar"

#if [ -f /usr/lib/libJavaReadline.so ]; then
#  BASE_FLAGS="$BASE_FLAGS -Djava.library.path=/usr/lib"
#  BASE_FLAGS="\$BASE_FLAGS -Dbsh.console.readlinelib=GnuReadline"
#  BASE_JARS="\$BASE_JARS libreadline-java.jar"
#fi

# Set parameters
set_jvm
set_classpath \$BASE_JARS
set_flags \$BASE_FLAGS
set_options \$BASE_OPTIONS

# Let's start
run "\$@"
EOF

cat > $RPM_BUILD_ROOT%{_bindir}/%{name}doc << EOF
#!/usr/bin/env %{_bindir}/%{name}
EOF
cat scripts/bshdoc.bsh >> $RPM_BUILD_ROOT%{_bindir}/%{name}doc

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post javadoc
rm -f %{_javadocdir}/%{name}
ln -s %{name}-%{version} %{_javadocdir}/%{name}

%postun javadoc
if [ "$1" = "0" ]; then
    rm -f %{_javadocdir}/%{name}
fi

%if %{gcj_support}
%post
%{update_gcjdb}

%postun
%{clean_gcjdb}
%endif

%files
%defattr(-,root,root)
%doc src/Changes.html src/License.txt src/README.txt
%attr(0755,root,root) %{_bindir}/%{name}
%attr(0755,root,root) %{_bindir}/%{name}doc
%{_javadir}/*
%dir %{_datadir}/%{name}

%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}
%endif

%files manual
%defattr(-,root,root)
%doc docs/*

%files javadoc
%defattr(-,root,root)
%{_javadocdir}/%{name}-%{version}

%files demo
%defattr(-,root,root)
%{_datadir}/%{name}/*

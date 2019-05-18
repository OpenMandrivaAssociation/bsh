%{?_javapackages_macros:%_javapackages_macros}

Name:           bsh
Version:        1.3.0
Release:        28
Summary:        Lightweight Scripting for Java
Group:		System/Libraries
License:        (SPL or LGPLv2+) and Public Domain
Source0:        %{name}-%{version}-src.tar.bz2
#cvs -d:pserver:anonymous@beanshell.cvs.sourceforge.net:/cvsroot/beanshell login
#cvs -z3 -d:pserver:anonymous@beanshell.cvs.sourceforge.net:/cvsroot/beanshell export -r rel_1_3_0_final BeanShell
#tar cjf bsh-1.3.0-src.tar.bz2 BeanShell
Source1:        bsh-1.3.0.pom
Source2:        bsh-bsf-1.3.0.pom
Source3:        %{name}-desktop.desktop

Patch0:         %{name}-build.patch
Patch1:         %{name}-xsl-fixes.patch
Patch2:		bsh-1.3.0-openjdk12.patch
BuildRequires:  java-devel
BuildRequires:  ant, bsf, imagemagick, desktop-file-utils
BuildRequires:  servlet
Requires:       java
Requires:       bsf
URL:            http://www.beanshell.org/
BuildArch:      noarch

%description
BeanShell is a small, free, embeddable, Java source interpreter with
object scripting language features, written in Java.  BeanShell
executes standard Java statements and expressions, in addition to
obvious scripting commands and syntax.  BeanShell supports scripted
objects as simple method closures like those in Perl and
JavaScript(tm).  You can use BeanShell interactively for Java
experimentation and debugging or as a simple scripting engine for your
applications.  In short: BeanShell is a dynamically interpreted Java,
plus some useful stuff.  Another way to describe it is to say that in
many ways BeanShell is to Java as Tcl/Tk is to C: BeanShell is
embeddable - You can call BeanShell from your Java applications to
execute Java code dynamically at run-time or to provide scripting
extensibility for your applications.  Alternatively, you can call your
Java applications and objects from BeanShell; working with Java
objects and APIs dynamically.  Since BeanShell is written in Java and
runs in the same space as your application, you can freely pass
references to "real live" objects into scripts and return them as
results.

%package manual
Summary:        Manual for %{name}

%description manual
Documentation for %{name}.

%package javadoc
Summary:        API documentation for %{name}

%description javadoc
This package provides %{summary}.

%package demo
Summary:        Demo for %{name}
AutoReqProv:    no
Requires:       %{name} = %{version}-%{release}

%description demo
Demonstrations and samples for %{name}.

%package utils
Summary:        %{name} utilities
Requires:       %{name} = %{version}-%{release}
Requires:       jline
Provides:       %{name}-desktop = %{version}-%{release}

%description utils
%{name} utilities.

%prep
%autosetup -p1 -n BeanShell
for j in $(find . -name "*.jar"); do
    mv $j $j.no
done
# remove all CVS files
for dir in `find . -type d -name CVS`; do rm -rf $dir; done
for file in `find . -type f -name .cvsignore`; do rm -rf $file; done
# fix rpmlint spurious-executable-perm warnings
for i in backbutton forwardbutton homebutton remoteconsole upbutton; do
    chmod 644 docs/images/$i.gif
done

%build
mkdir -p lib
pushd lib
ln -sf $(build-classpath bsf)
ln -sf $(build-classpath servlet)
popd
ant="ant -Dant.build.javac.source=12"
$ant test dist
(cd docs/faq && $ant)
(cd docs/manual && $ant)

%install
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
for mod in '' bsf classpath commands core reflect util; do
    install -p -m 644 dist/%{name}${mod:+-${mod}}-%{version}.jar \
             $RPM_BUILD_ROOT%{_javadir}/%{name}${mod:+-${mod}}.jar
done

# poms
install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -pm 644 %{SOURCE1} \
    $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}.pom
install -pm 644 %{SOURCE2} \
    $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{name}-bsf.pom

%add_maven_depmap JPP-%{name}.pom %{name}.jar -a org.beanshell:%{name}
%add_maven_depmap JPP-%{name}-bsf.pom %{name}-bsf.jar

# manual
find docs -name ".cvswrappers" -exec rm -f {} \;
find docs -name "*.xml" -exec rm -f {} \;
find docs -name "*.xsl" -exec rm -f {} \;
find docs -name "*.log" -exec rm -f {} \;
(cd docs/manual && mv html/* .)
(cd docs/manual && rm -rf html)
(cd docs/manual && rm -rf xsl)
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}
cp -pr javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}
# menu entry
desktop-file-install --mode=644 \
  --dir=$RPM_BUILD_ROOT%{_datadir}/applications %{SOURCE3}
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/16x16/apps
convert src/bsh/util/lib/icon.gif \
  $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/16x16/apps/bsh.png

# demo
for i in `find tests -name \*.bsh`; do
  perl -p -i -e 's,^\n?#!(/(usr/)?bin/java bsh\.Interpreter|/bin/sh),#!/usr/bin/env %{_bindir}/%{name},' $i
  if head -1 $i | grep '#!/usr/bin/env %{_bindir}/%{name}' >/dev/null; then
    chmod 755 $i
  fi
done
chmod 755 tests/Template
cat > one << EOF
#!/bin/sh

EOF
cat tests/Interactive/reload/one >> one
cat one > tests/Interactive/reload/one
rm one
cat > two << EOF
#!/bin/sh

EOF
cat tests/Interactive/reload/two >> two
cat two > tests/Interactive/reload/two
rm two
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -pr tests $RPM_BUILD_ROOT%{_datadir}/%{name}
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/%{name}/webapps
install -m 644 dist/bshservlet.war $RPM_BUILD_ROOT%{_datadir}/%{name}/webapps
install -m 644 dist/bshservlet-wbsh.war $RPM_BUILD_ROOT%{_datadir}/%{name}/webapps

# scripts
install -d $RPM_BUILD_ROOT%{_bindir}

%jpackage_script bsh.Interpreter "\${BSH_DEBUG:+-Ddebug=true}" jline.ConsoleRunner %{name}:jline %{name} true
%jpackage_script bsh.Console "\${BSH_DEBUG:+-Ddebug=true}" "" %{name} %{name}-console true

cat > $RPM_BUILD_ROOT%{_bindir}/%{name}doc << EOF
#!/usr/bin/env %{_bindir}/%{name}
EOF
cat scripts/bshdoc.bsh >> $RPM_BUILD_ROOT%{_bindir}/%{name}doc

%files -f .mfiles
%doc src/License.txt
%doc src/Changes.html src/README.txt
%{_javadir}/*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/webapps

%files manual
%doc src/License.txt
%doc docs/*

%files javadoc
%doc src/License.txt
%{_javadocdir}/%{name}

%files demo
%doc tests/README.txt tests/Interactive/README
%{_datadir}/%{name}/*

%files utils
%attr(0755,root,root) %{_bindir}/%{name}*
%{_datadir}/applications/%{name}-desktop.desktop
%{_datadir}/icons/hicolor/*x*/apps/%{name}.png

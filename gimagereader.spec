#
# FIXME: clang fails at linking time because it 
#	 still has some probems with openmp
#

%define tname gImageReader
%define oname %(echo %{tname} | tr [:upper:] [:lower:] )

Summary:	A graphical frontend to tesseract-ocr
Name:		%{oname}
Version:	3.1.2
Release:	0
License:	GPLv3+
Group:		Office
URL:		https://github.com/manisandro/%{name}
Source0:	https://github.com/manisandro/%{tname}/releases/download/v%{version}/%{name}-%{version}.tar.xz

BuildRequires:	appstream-util
BuildRequires:	cmake
BuildRequires:	desktop-file-utils
BuildRequires:	gettext
BuildRequires:	intltool
BuildRequires:	pkgconfig(tesseract)
BuildRequires:	pkgconfig(sane-backends)
#BuildRequires:	libappstream-glib
# gtk interface
BuildRequires:	pkgconfig(cairomm-1.0)
BuildRequires:	pkgconfig(gtkmm-3.0)
BuildRequires:	pkgconfig(gtksourceviewmm-3.0)
BuildRequires:	pkgconfig(gtkspellmm-3.0) >= 3.0.4
BuildRequires:	pkgconfig(poppler-glib)
# qt4 interface
BuildRequires:	pkgconfig(poppler-qt4)
BuildRequires:	pkgconfig(QtCore)
BuildRequires:	pkgconfig(QtSpell-qt4)
# qt5 interface
BuildRequires:	pkgconfig(poppler-qt5)
BuildRequires:	pkgconfig(Qt5Widgets)
BuildRequires:	pkgconfig(QtSpell-qt5)
#BuildRequires:	qt5-devel

Requires:	hicolor-icon-theme

%description
# from the homepage
gImageReader is a simple front-end to tesseract. Features include:

  · Automatic page layout detection
  · User can manually define and adjust recognition regions
  · Import images from disk, scanning devices, clipboard and screenshots
  . Supports multipage PDF documents
  · Recognized text displayed directly next to the image
  · Basic editing of output text, including search/replace and removing
    line breaks
  · Spellchecking for output text (if corresponding dictionary installed)

#----------------------------------------------------------------------------

%package gtk
Summary:	A Gtk+ front-end to tesseract-ocr
Requires:	%{name}-shared = %{version}-%{release}

%description gtk
gImageReader is a simple front-end to tesseract. Features include:

  · Automatic page layout detection
  · User can manually define and adjust recognition regions
  · Import images from disk, scanning devices, clipboard and screenshots
  . Supports multipage PDF documents
  · Recognized text displayed directly next to the image
  · Basic editing of output text, including search/replace and removing
    line breaks
  · Spellchecking for output text (if corresponding dictionary installed)

This package contains the Gtk+ front-end.

%files gtk
%{_bindir}/%{name}-gtk
%{_datadir}/appdata/%{name}-gtk.appdata.xml
%{_datadir}/applications/%{name}-gtk.desktop
%{_datadir}/glib-2.0/schemas/org.gnome.%{name}.gschema.xml

#----------------------------------------------------------------------------

%package qt4
Summary:	A Qt4 front-end to tesseract-ocr
Requires:	%{name}-shared = %{version}-%{release}

%description qt4
gImageReader is a simple front-end to tesseract. Features include:

  · Automatic page layout detection
  · User can manually define and adjust recognition regions
  · Import images from disk, scanning devices, clipboard and screenshots
  . Supports multipage PDF documents
  · Recognized text displayed directly next to the image
  · Basic editing of output text, including search/replace and removing
    line breaks
  · Spellchecking for output text (if corresponding dictionary installed)

This package contains the Qt4 front-end.

%files qt4
%{_bindir}/%{name}-qt4
%{_datadir}/appdata/%{name}-qt4.appdata.xml
%{_datadir}/applications/%{name}-qt4.desktop

#----------------------------------------------------------------------------

%package qt5
Summary:	A Qt5 front-end to tesseract-ocr
Requires:	%{name}-shared = %{version}-%{release}

%description qt5
gImageReader is a simple front-end to tesseract. Features include:

  · Automatic page layout detection
  · User can manually define and adjust recognition regions
  · Import images from disk, scanning devices, clipboard and screenshots
  . Supports multipage PDF documents
  · Recognized text displayed directly next to the image
  · Basic editing of output text, including search/replace and removing
    line breaks
  · Spellchecking for output text (if corresponding dictionary installed)

This package contains the Qt5 front-end.

%files qt5
%{_bindir}/%{name}-qt5
%{_datadir}/appdata/%{name}-qt5.appdata.xml
%{_datadir}/applications/%{name}-qt5.desktop

#----------------------------------------------------------------------------

%package shared
Summary:	Shared files for %{name}
BuildArch:	noarch

%description shared
Shared files files for %{name}.

%files shared -f %{name}.lang
%{_datadir}/icons/hicolor/48x48/apps/%{name}.png
%{_datadir}/icons/hicolor/128x128/apps/%{name}.png
%{_datadir}/icons/hicolor/256x256/apps/%{name}.png
%doc README
%doc README.md
%doc NEWS
%doc TODO
%doc AUTHORS
%doc ChangeLog
%doc COPYING

#----------------------------------------------------------------------------

%prep
%setup -q

# -std=c++11 is not compatible with clang (but only with clang++)
%__sed -i -e '/ADD_DEFINITIONS(-std=c++11)/d' CMakeLists.txt

# set gtk, qt4 and qt5 branch
mkdir build-gtk
%__find . -maxdepth 1 -mindepth 1	\
	-not -name ./build-gtk		\
	-and -not -name README		\
	-and -not -name README.md	\
	-and -not -name NEWS		\
	-and -not -name TODO		\
	-and -not -name AUTHORS		\
	-and -not -name ChangeLog	\
	-and -not -name COPYING		\
	-exec mv -t ./build-gtk '{}' \;
cp -a build-gtk build-qt4
cp -a build-gtk build-qt5

%build
# -std=c++11 is not compatible with clang (but only with clang++)
#export CXXFLAGS="${optflags} -std=c++11" #-fopenmp
#export CFLAGS="${optflags} -fopenmp"

export CC=gcc
export CXX=g++

# build
for i in gtk qt4 qt5
do
	pushd build-$i
	%cmake \
		-DINTERFACE_TYPE=$i			\
		-DENABLE_VERSIONCHECK:BOOL=FALSE	\
		-DMANUAL_DIR="%{_docdir}/%{name}-shared"
	%make
	popd
done

%install
for i in gtk qt4 qt5
do
	%make_install -C build-$i/build
done

# locale files
%find_lang %{name} --with-man

%check
# .desktop file
for i in gtk qt4 qt5
do
	desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}-$i.desktop
done

# AppStream metadata
for i in gtk qt4 qt5
do
	appstream-util validate-relax --nonet %{buildroot}%{_datadir}/appdata/%{name}-$i.appdata.xml
done

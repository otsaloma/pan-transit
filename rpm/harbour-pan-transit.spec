# Prevent brp-python-bytecompile from running.
%define __os_install_post %{___build_post}

# "Harbour RPM packages should not provide anything."
%define __provides_exclude_from ^%{_datadir}/.*$

Name: harbour-pan-transit
Version: 0.1
Release: 1
Summary: Departures from public transportation stops
License: GPLv3+
URL: http://github.com/otsaloma/pan-transit
Source: %{name}-%{version}.tar.xz
BuildArch: noarch
BuildRequires: gettext
BuildRequires: make
BuildRequires: qt5-qttools-linguist
Requires: libsailfishapp-launcher
Requires: pyotherside-qml-plugin-python3-qt5 >= 1.2
Requires: qt5-qtdeclarative-import-positioning >= 5.2
Requires: sailfishsilica-qt5

%description
Pan Transit is an application for Sailfish OS to view departures from
public transport stops. It is designed to support multiple different
providers (i.e. cities/regions).

%prep
%setup -q

%install
make DESTDIR=%{buildroot} PREFIX=/usr install

%files
%defattr(-,root,root,-)
%{_datadir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png

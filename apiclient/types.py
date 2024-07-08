# -*- coding: utf-8 -*-

# HOSTVM VDI 3.5

from dataclasses import dataclass, field

# Providers

@dataclass
class Provider:
    name: str
    tags: list = field(default_factory=list)
    comments: str = ''

@dataclass
class PhysicalMachinesServiceProvider(Provider):
    '''Static IP Machines Provider'''
    type: str = 'PhysicalMachinesServiceProvider'
    config: str = ''

@dataclass
class oVirtPlatform(Provider):
    '''oVirt/RHEV Platform Provider'''
    type: str = 'oVirtPlatform'
    ovirtVersion: str = '4'
    host: str = ''  # *
    username: str = 'admin@internal'
    password: str = ''  # *
    maxPreparingServices: str = '10'
    maxRemovingServices: str = '5'
    timeout: str = '10'
    macsRange: str = '52:54:00:00:00:00-52:54:00:FF:FF:FF'

# Services

@dataclass
class Service:
    name: str
    tags: list = field(default_factory=list)
    comments: str = ''
    proxy_id: str = '-1'

@dataclass
class IPMachinesService(Service):
    '''Static Multiple IP'''
    ipList: list = field(default_factory=list)
    token: str = ''
    port: str = '0'
    skipTimeOnFailure: str = '0'
    maxSessionForMachine: str = '0'
    lockByExternalAccess: str = 'False'

@dataclass
class oVirtLinkedService(Service):
    '''oVirt/RHEV Linked Clone'''
    cluster: str = ''  # *
    datastore: str = ''  # *
    minSpaceGB: str = '32'
    machine: str = ''  # *
    memory: str = '512'
    memoryGuaranteed: str = '256'
    usb: str = ''
    display: str = ''
    baseName: str = ''  # *
    lenName: str = '5'

# Authenticators

@dataclass
class Authenticator:
    name: str
    small_name: str
    tags: list = field(default_factory=list)
    comments: str = ''
    priority: int = 1
    visible: bool = True

@dataclass
class ActiveDirectoryAuthenticator(Authenticator):
    '''Active Directory'''
    type: str = 'ActiveDirectoryAuthenticator'
    host: str = ''  # *
    username: str = ''  # *
    password: str = ''  # *
    ldapBase: str = ''  # *
    ssl: str = 'False'
    timeout: str = '10'
    groupBase: str = ''
    defaultDomain: str = ''
    nestedGroups: str = 'False'

@dataclass
class InternalDBAuth(Authenticator):
    '''Internal Database'''
    type: str = 'InternalDBAuth'

@dataclass
class SimpleLdapAuthenticator(Authenticator):
    '''Simple LDAP'''
    type: str = 'SimpleLdapAuthenticator'

@dataclass
class RegexLdapAuthenticator(Authenticator):
    '''Regex LDAP'''
    type: str = 'RegexLdapAuthenticator'

@dataclass
class SAML20Authenticator(Authenticator):
    '''SAML'''
    type: str = 'SAML20Authenticator'

# OS managers

@dataclass
class OSManager:
    name: str
    tags: list = field(default_factory=list)
    comments: str = ''

@dataclass
class LinuxManager(OSManager):
    '''Linux OS Manager'''
    type: str = 'LinuxManager'
    onLogout: str = 'keep'
    idle: str = '-1'
    deadLine: str = 'True'

@dataclass
class LinRandomPasswordManager(LinuxManager):
    '''Linux Random Password OS Manager'''
    type: str = 'LinRandomPasswordManager'
    userAccount: str = ''  # *

@dataclass
class WindowsManager(OSManager):
    '''Windows Basic OS Manager'''
    type: str = 'WindowsManager'
    onLogout: str = 'keep'
    idle: str = '-1'
    deadLine: str = 'True'

@dataclass
class WinRandomPasswordManager(WindowsManager):
    '''Windows Random Password OS Manager'''
    type: str = 'WinRandomPasswordManager'
    userAccount: str = ''  # *
    password: str = ''  # *

@dataclass
class WinDomainManager(WindowsManager):
    '''Windows Domain OS Manager'''
    type: str = 'WinDomainManager'
    domain: str = ''  # *
    ou: str = ''
    account: str = ''  # *
    password: str = ''  # *
    grp: str = ''
    serverHint: str = ''
    ssl: str = 'True'
    removeOnExit: str = 'True'

# Transports

@dataclass
class Transport:
    name: str
    tags: list = field(default_factory=list)
    comments: str = ''
    priority: int = 1
    nets_positive: bool = True
    label: str = ''
    networks: list = field(default_factory=list)
    allowed_oss: list = field(default_factory=list)
    pools: list = field(default_factory=list)

@dataclass
class RDPTransport(Transport):
    '''RDP direct'''
    type: str = 'RDPTransport'
    useEmptyCreds: str = 'False'
    fixedName: str = ''
    fixedPassword: str = ''
    withoutDomain: str = 'False'
    fixedDomain: str = ''
    allowSmartcards: str = 'False'
    allowPrinters: str = 'False'
    allowDrives: str = 'False'
    enforceDrives: str = ''
    allowSerials: str = 'False'
    allowClipboard: str = 'True'
    allowAudio: str = 'True'
    allowWebcam: str = 'False'
    usbRedirection: str = 'False'
    wallpaper: str = 'False'
    multimon: str = 'False'
    aero: str = 'False'
    smooth: str = 'True'
    showConnectionBar: str = 'True'
    credssp: str = 'True'
    rdpPort: str = '3389'
    screenSize: str = '-1x-1'
    colorDepth: str = '24'
    alsa: str = 'False'
    multimedia: str = 'False'
    printerString: str = ''
    smartcardString: str = ''
    customParameters: str = ''
    allowMacMSRDC: str = 'False'
    customParametersMAC: str = ''

@dataclass
class TSRDPTransport(RDPTransport):
    '''RDP tunnel'''
    type: str = 'TSRDPTransport'
    tunnelServer: str = ''
    tunnelWait: str = '60'
    verifyCertificate: str = 'False'

@dataclass
class RATransport(RDPTransport):
    '''RemoteApp direct'''
    type: str = 'RATransport'
    fixedApp: str = ''  # *

@dataclass
class TRATransport(TSRDPTransport):
    '''RemoteApp tunnel'''
    type: str = 'TRATransport'
    fixedApp: str = ''  # *

@dataclass
class HTML5RDPTransport(Transport):
    '''HTML5 RDP'''
    type: str = 'HTML5RDPTransport'
    guacamoleServer: str = 'https://'
    useGlyptodonTunnel: str = 'False'
    useEmptyCreds: str = 'False'
    fixedName: str = ''
    fixedPassword: str = ''
    withoutDomain: str = 'False'
    fixedDomain: str = ''
    wallpaper: str = 'False'
    desktopComp: str = 'False'
    smooth: str = 'False'
    enableAudio: str = 'True'
    enableAudioInput: str = 'False'
    enablePrinting: str = 'False'
    enableFileSharing: str = 'False'
    enableClipboard: str = 'enabled'
    serverLayout: str = '-'
    ticketValidity: str = '60'
    forceNewWindow: str = 'False'
    security: str = 'any'
    rdpPort: str = '3389'
    customGEPath: str = '/'

@dataclass
class HTML5RATransport(Transport):
    '''HTML5 RemoteApp'''
    type: str = 'HTML5RATransport'
    guacamoleServer: str = 'https://'
    useEmptyCreds: str = 'False'
    fixedName: str = ''
    fixedPassword: str = ''
    withoutDomain: str = 'False'
    fixedDomain: str = ''
    fixedApp: str = ''  # *
    wallpaper: str = 'False'
    desktopComp: str = 'False'
    smooth: str = 'False'
    enableAudio: str = 'False'
    enableAudioInput: str = 'False'
    enablePrinting: str = 'False'
    enableFileSharing: str = 'False'
    enableClipboard: str = 'enabled'
    serverLayout: str = '-'
    ticketValidity: str = '60'
    forceNewWindow: str = 'False'
    security: str = 'any'
    rdpPort: str = '3389'

@dataclass
class PCoIPTransport(Transport):
    '''PCoIP Cloud Access'''
    type: str = 'PCoIPTransport'
    fixedName: str = ''
    fixedPassword: str = ''
    fixedDomain: str = ''

@dataclass
class SPICETransport(Transport):
    '''SPICE direct'''
    type: str = 'SPICETransport'
    serverCertificate: str = ''
    fullScreen: str = 'False'
    usbShare: str = 'False'
    autoNewUsbShare: str = 'False'
    smartCardRedirect: str = 'False'

@dataclass
class TSSPICETransport(SPICETransport):
    '''SPICE tunnel'''
    type: str = 'TSSPICETransport'
    tunnelServer: str = ''  # *
    tunnelWait: str = '30'
    verifyCertificate: str = 'False'

@dataclass
class URLTransport(Transport):
    '''URL Launcher'''
    type: str = 'URLTransport'
    urlPattern: str = 'https://pvhostvm.ru'
    forceNewWindow: str = 'False'

@dataclass
class X2GOTransport(Transport):
    '''X2Go direct'''
    type: str = 'X2GOTransport'
    fixedName: str = ''
    screenSize: str = 'F'
    desktopType: str = 'XFCE'
    customCmd: str = ''
    sound: str = 'True'
    exports: str = 'False'
    speed: str = '3'
    soundType: str = 'pulse'
    keyboardLayout: str = ''
    pack: str = '16m-jpeg'
    quality: str = '6'

@dataclass
class TX2GOTransport(X2GOTransport):
    '''X2Go tunnel'''
    type: str = 'TX2GOTransport'
    tunnelServer: str = ''  # *
    tunnelWait: str = '30'
    verifyCertificate: str = 'False'

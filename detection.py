def get_compression(data):
    if len(data) == 0:
        return 'none'
    elif data[:2] == bytes([0x1D, 0x04]) or data[:2] == bytes([0x15, 0x23]):
        return 'rot'
    elif data[0:8] == b"NXS3\x03\x00\x00\x01":
        return 'nxs3'
    elif data[:4] == bytes([0x50, 0x4B, 0x03, 0x04]) or data[:4] == bytes([0x50, 0x4B, 0x05, 0x06]):
        return 'zip'
    return 'none'

def get_ext(data):
    if len(data) == 0:
        return 'empty'
    elif data[:3] == b'PVR':
        return 'pvr'
    elif data[:4] == bytes([0x34, 0x80, 0xC8, 0xBB]):
        return 'mesh'
    elif data[:4] == b'RIFF':
        return 'wem'
    elif data[:8] == b'RAWANIMA':
        return 'rawanimation'
    elif data[:8] == b'NEOXBIN1':
        return 'uiprefab'
    elif data[:8] == b'SKELETON':
        return 'skeleton'
    elif data[1:8] == bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]):
        return 'blasttool'
    elif data[:6] == bytes([0x01, 0x00, 0x05, 0x00, 0x00, 0x00]):
        return 'foliage'
    elif data[:8] == b'NEOXMESH':
        return 'uimesh'
    elif data[:33] == b'NVidia(r) GameWorks Blast(tm) v.1':
        return 'blast'
    elif data[:4] == bytes([0xE3, 0x00, 0x00, 0x00]) or data[:4] == bytes([0x63, 0x00, 0x00, 0x00]) or data[2:4] == bytes([0x0D, 0x0A]):
        return 'pyc'
    elif data[:12] == b'CocosStudio-UI':
        return 'coc'
    elif data[:4] == bytes([0x13, 0xAB, 0xA1, 0x5C]):
        return 'astc'
    elif data[:3] == b'hit':
        return 'hit'
    elif data[:3] == b'PKM':
        return 'pkm'
    elif data[:3] == b'DDS':
        return 'dds'
    elif data[-18:-2] == b'TRUEVISION-XFILE' or data[:3] == bytes([0x00, 0x00, 0x02]) or data[:3] == bytes([0x0D, 0x00, 0x02]):
        return 'tga'
    elif data [:2] == b'BM':
        return 'bmp'
    elif data[:18] == b'from typing import ':
        return 'pyi'
    elif data[1:4] == b'KTX':
        return 'ktx'
    elif data[:9] == b'blastmesh':
        return 'blastmesh'
    elif data[:10] == b'clothasset':
        return 'clothasset'
    elif data[1:4] == b'PNG':
        return 'png'
    elif data[:4] == b'VANT':
        return 'vant'
    elif data[:4] == b'MDMP':
        return 'mdmp'
    elif data[:4] == b'RGIS':
        return 'gis'
    elif data[:4] == b'NTRK':
        return 'trk'
    elif data[:4] == bytes([0xFF,0xD8,0xFF,0xE1]):
        return 'jpg'
    elif data[:4] == b'BKHD':
        return 'bnk'
    elif data[:27] == b'-----BEING PUBLIC KEY-----':
        return 'pem'
    elif data[:1] == b'%':
        return 'tpl'
    elif data[:4] == b'TZif':
        return 'tzif'
    elif data[6:10] == b'JFIF':
        return 'jfif'
    elif data[4:8] == b'ftyp':
        return 'mp4'
    elif len(data) < 100000000:
        #NeoXML file detection
        if b'<Material' in data:
            return 'mtl'
        if b'<MaterialGroup' in data:
            return 'mtg'
        if b'<MetaInfo' in data:
            return 'pvr.meta'
        if b'ViewProjection' in data:
            return 'binary'
        if b'<Section' in data:
            return 'sec'
        if b'GeoBatchHint="1"' in data:
            return 'gim'
        if b'<Track' in data:
            return 'trackgroup'
        if b'<Instances' in data:
            return 'decal'
        if b'<Physics' in data:
            return 'col'
        if b'<LODPolicy' in data or b'<LODProfile' in data:
            return 'lod'
        if b'Type="Animation"' in data:
            return 'animation'
        if b'DisableBakeLightProbe=' in data:
            return 'prefab'
        if b'<Scene' in data:
            return 'scn'
        if b'"ParticleSystemTemplate"' in data:
            return 'pse'
        if b'<MainBody' in data:
            return 'nxcompute'
        if b'?xml' in data:
            return 'xml'
        if b'<MapSkeletonToMeshBone' in data:
            return 'skeletonextra'
        if b'<ShadingModel' in data:
            return 'nxshader'
        if b'<BlastDynamic' in data:
            return 'blt'
        if b'"ParticleAudio"' in data:
            return 'psemusic'
        if b'<BlendSpace' in data and b'is2D="false"' in data:
            return 'blendspace1d'
        if b'<AnimationConfig' in data:
            return 'animconfig'
        if b'<AnimationGraph' in data:
            return 'animgraph'
        if b'<Head Type="Timeline"' in data:
            return 'timeline'
        if b'<Chain' in data:
            return 'physicalbone'
        if b'<BlendSpace' in data and b'is2D="true"' in data:
            return 'blendspace'
        if b'<PostProcess' in data:
            return 'postprocess'
        if b'"mesh_import_options":{' in data:
            return 'nxmeta'
        if b'<SceneConfig' in data:
            return 'scnex'
        if b'<LocalPoints' in data:
            return 'localweather'
        if b'GeoBatchHint="0"' in data:
            return 'gimext'
        if b'"AssetType":"HapticsData"' in data:
            return 'haptic'
        if b'<LocalFogParams' in data:
            return 'localfogparams'
        if b'<Audios' in data or b'<AudioSource':
            return 'prefabaudio'
        if b'"ReferenceSkeleton' in data:
            return 'featureschema'
        if b'<Relationships' in data:
            return 'xml.rels'
        if b'<Waterfall' in data:
            return 'waterfall'
        if b'"ReferenceSkeletonPath"' in data:
            return 'mirrortable'
        if b'<ClothAsset' in data:
            return 'clt'
        if b'<plist' in data:
            return 'plist'
        if b'<ShaderCompositor' in data or "<ShaderFeature" in data or "<ShaderIndexes" in data or "<RenderTrigger" in data:
            return 'render'
        if b'<SkeletonRig' in data:
            return 'skeletonrig'
        if b'format: ' in data and b'filter: ' in data:
            return 'atlas'
        if b'<ShaderCache' in data:
            return 'cache'
        if b'char' in data and 'width=' in data and 'height=' in data:
            return 'fnt'
        if b'<AllCaches' in data:
            return 'info'
        if b'<AllPreloadCaches' in data:
            return 'list'
        if b'<Remove_Files' in data:
            return 'map'
        if b'<HLSL File="' in data:
            return 'md5'
        if b'<EnvParticle' in data:
            return 'envp'
        if b'<FxGroup' in data:
            return 'sfx'
        if b'#?RADIANCE' in data:
            return 'hdr'
        if b'<Macros' in data:
            return 'xml.template'
        if b'precision mediump' in data:
            return 'ps'
        if b'POSITION' in data:
            return 'vs'
        if b'technique' in data:
            return 'nfx'
        if b'package google.protobuf' in data:
            return 'proto'
        if b'#ifndef' in data:
            return 'h'
        if b'#include <google/protobuf' in data:
            return "cc"
        if b'void' in data or b'main(' in data or b'include' in data or b'float' in data:
            return 'shader'
        if b'technique' in data or b'ifndef' in data:
            return 'shader'
        if b'<script' in data:
            return 'html'
        if b'Javascript' in data:
            return 'js'
        if b'biped' in data or b'bip001' in data or b'bone' in data or b'bone001' in data or b'bip01' in data:
            return 'bip'
        if b'div.document' in data:
            return 'css'
    elif data[:1] == b'{':
        return 'json'
    return 'dat'

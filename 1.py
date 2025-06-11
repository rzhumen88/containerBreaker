from anytree import Node, RenderTree, PreOrderIter

a = ['2d/school.mlp', '2d/side/bettymine.img', '2d/side/bloodfront.aan', '2d/side/bloodleft.aan', '2d/side/bloodpool.aan', '2d/side/bloodright.aan', '2d/side/bouy.bmp', '2d/side/box.img', '2d/side/brainsplat.aan', '2d/side/demon.bmp', '2d/side/dispenser.bmp', '2d/side/explo.aan', '2d/side/fire.aan', '2d/side/gexplo.aan', '2d/side/muzzleflare.aan', '2d/side/nnet.bmp', '2d/side/proxmine.img', '2d/side/pylon.bmp', '2d/side/remotemine.img', '2d/side/ricochet.aan', '2d/side/shadow.img', '2d/side/smallfire.aan', '2d/side/smallshadow.img', '2d/side/smoke.aan', '2d/side/soundsatellite.bmp', '2d/side/soundthing.bmp', '2d/side/target.img', '2d/side/timemine.img', '2d/side/tinyfire.aan', '2d/side/tinysmoke.aan', '2d/side/warp.bmp', '2d/top/bettymine.img', '2d/top/bloodfront.aan', '2d/top/bloodleft.aan', '2d/top/bloodpool.aan', '2d/top/bloodright.aan', '2d/top/bouy.bmp', '2d/top/box.img', '2d/top/brainsplat.aan', '2d/top/demon.bmp', '2d/top/dispenser.bmp', '2d/top/explo.aan', '2d/top/fire.aan', '2d/top/gexplo.aan', '2d/top/muzzleflare.aan', '2d/top/nnet.bmp', '2d/top/proxmine.img', '2d/top/pylon.bmp', '2d/top/remotemine.img', '2d/top/ricochet.aan', '2d/top/shadow.img', '2d/top/smallfire.aan', '2d/top/smallshadow.img', '2d/top/smoke.aan', '2d/top/soundsatellite.bmp', '2d/top/soundthing.bmp', '2d/top/target.img', '2d/top/timemine.img', '2d/top/tinyfire.aan', '2d/top/tinysmoke.aan', '2d/top/warp.bmp', '3d/ammo.bounds', '3d/ammo.mesh', '3d/ammo.sop', '3d/ammo.tex', '3d/autorifle.bounds', '3d/autorifle.mesh', '3d/autorifle.sop', '3d/autorifle.tex', '3d/backpack.bounds', '3d/backpack.mesh', '3d/backpack.sop', '3d/backpack.tex', '3d/backpack_backpack.trans', '3d/backpackicon.bounds', '3d/backpackicon.mesh', '3d/backpackicon.sop', '3d/backpackicon.tex', '3d/bandg_blownup.bounds', '3d/bandg_blownup.mesh', '3d/bandg_blownup.sop', '3d/bandg_blownup.tex', '3d/bandg_blownup_bandguy.event', '3d/bandg_blownup_instrument.trans', '3d/bandg_march.bounds', '3d/bandg_march.mesh', '3d/bandg_march.sop', '3d/bandg_march.tex', '3d/bandg_march_bandguy.event', '3d/bandg_march_instrument.trans', '3d/bandg_onfire.bounds', '3d/bandg_onfire.mesh', '3d/bandg_onfire.sop', '3d/bandg_onfire.tex', '3d/bandg_onfire_bandguy.event', '3d/bandg_onfire_instrument.trans', '3d/bandg_run.bounds', '3d/bandg_run.mesh', '3d/bandg_run.sop', '3d/bandg_run.tex', '3d/bandg_run_bandguy.event', '3d/bandg_run_instrument.trans', '3d/bandg_shot.bounds', '3d/bandg_shot.mesh', '3d/bandg_shot.sop', '3d/bandg_shot.tex', '3d/bandg_shot_bandguy.event', '3d/bandg_shot_instrument.trans', '3d/bandg_stand.bounds']


root = Node('root')

for b in a:
    Node(b, parent=root)


print(RenderTree(root))

for node in PreOrderIter(root):
    print(node)

package com.mrcrayfish.vehicle.paper.recovery;

import org.bukkit.Bukkit;
import org.bukkit.World;
import org.bukkit.entity.Entity;
import org.bukkit.util.BoundingBox;
import org.bukkit.util.Vector;

import java.util.List;
import java.util.Set;
import java.util.UUID;

/** Experimental conservative obstacle query for an already routed cable.
 * Coordinates must be WORLD coordinates, not the truck's model coordinates.
 * Does not validate the truck, target body, region permissions, cable sweep
 * between ticks, or endpoints; callers must do those separately. */
public final class RecoveryCableWorldCheck {
    private RecoveryCableWorldCheck() { }
    private static final double MAX_RADIUS = .1, MAX_LENGTH = 32;

    public static boolean clear(World world, List<RecoveryCable.Point> points, double radius, Set<UUID> excludedEntities) {
        if (!Bukkit.isPrimaryThread() || world == null || points == null || points.size()<2 || points.size()>3
                || !Double.isFinite(radius) || radius<0 || radius>MAX_RADIUS || excludedEntities==null
                || excludedEntities.stream().anyMatch(java.util.Objects::isNull)) return false;
        try {
            for (int i=1;i<points.size();i++) {
                var a=points.get(i-1); var b=points.get(i);
                if(a==null || b==null) return false;
                Vector start=new Vector(a.x(),a.y(),a.z()), end=new Vector(b.x(),b.y(),b.z());
                if(start.distanceSquared(end)<1e-10 || start.distanceSquared(end)>MAX_LENGTH*MAX_LENGTH) return false;
                BoundingBox bounds=new BoundingBox(Math.min(a.x(),b.x())-radius,Math.min(a.y(),b.y())-radius,
                        Math.min(a.z(),b.z())-radius,Math.max(a.x(),b.x())+radius,
                        Math.max(a.y(),b.y())+radius,Math.max(a.z(),b.z())+radius);
                if(bounds.getMinY()<world.getMinHeight() || bounds.getMaxY()>=world.getMaxHeight()
                        || bounds.getMinX() < -30000000 || bounds.getMaxX()>30000000
                        || bounds.getMinZ() < -30000000 || bounds.getMaxZ()>30000000) return false;
                int minX=(int)Math.floor(bounds.getMinX()),maxX=(int)Math.floor(bounds.getMaxX());
                int minY=(int)Math.floor(bounds.getMinY()),maxY=(int)Math.floor(bounds.getMaxY());
                int minZ=(int)Math.floor(bounds.getMinZ()),maxZ=(int)Math.floor(bounds.getMaxZ());
                if ((long)(maxX-minX+1)*(maxY-minY+1)*(maxZ-minZ+1)>4096) return false;
                for(int x=minX>>4;x<=maxX>>4;x++) for(int z=minZ>>4;z<=maxZ>>4;z++)
                    if(!world.isChunkLoaded(x,z)) return false;
                for(int x=minX;x<=maxX;x++) for(int y=minY;y<=maxY;y++) for(int z=minZ;z<=maxZ;z++) {
                    var block=world.getBlockAt(x,y,z);
                    if(block.getType().isAir())continue;
                    var boxes=block.getCollisionShape().getBoundingBoxes();
                    if(boxes.isEmpty()) {
                        // Treat fluids and non-collidable blocks as full obstacles.
                        if(intersects(start,end,new BoundingBox(x,y,z,x+1,y+1,z+1).expand(radius)))return false;
                    } else for(var box:boxes)
                        if(intersects(start,end,box.clone().shift(x,y,z).expand(radius)))return false;
                }
                for(Entity entity:world.getNearbyEntities(bounds))
                    if(entity.isValid() && !excludedEntities.contains(entity.getUniqueId())
                            && intersects(start,end,entity.getBoundingBox().clone().expand(radius))) return false;
            }
            return true;
        } catch(RuntimeException e) { return false; }
    }

    /** Finite segment against closed box, including tangency. */
    static boolean intersects(Vector start, Vector end, BoundingBox box) {
        double lo=0,hi=1;
        double[] a={start.getX(),start.getY(),start.getZ()}, b={end.getX(),end.getY(),end.getZ()};
        double[] min={box.getMinX(),box.getMinY(),box.getMinZ()}, max={box.getMaxX(),box.getMaxY(),box.getMaxZ()};
        for(int i=0;i<3;i++) {
            double d=b[i]-a[i];
            if(Math.abs(d)<1e-12) { if(a[i]<min[i] || a[i]>max[i]) return false; continue; }
            double x=(min[i]-a[i])/d, y=(max[i]-a[i])/d;
            lo=Math.max(lo,Math.min(x,y));hi=Math.min(hi,Math.max(x,y));
            if(lo>hi)return false;
        }
        return true;
    }
}

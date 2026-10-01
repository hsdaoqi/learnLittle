/**
 * 2.5D 等距微立体插画场景（共享组件）
 *
 * 用于登录页、注册页等认证页面的左侧插画区。
 * 包含：几何背景块面、Q版机器人、三层同心圆平台、6个环绕图标节点、SVG连接线。
 */

import { Shield, Camera, Folder, Monitor, Cloud, Globe } from 'lucide-react';

/* ─────────────────────────────────────────────
   2.5D 等距几何背景块面
───────────────────────────────────────────── */
export function GeometricBackground() {
  const blocks = [
    { w: 320, h: 140, top: '0%', left: '3%', rot: 6, color: 'var(--color-geo-1)', r: 24 },
    { w: 200, h: 180, top: '55%', left: '0%', rot: -4, color: 'var(--color-geo-2)', r: 20 },
    { w: 160, h: 240, top: '5%', left: '28%', rot: -8, color: 'var(--color-geo-3)', r: 18 },
    { w: 240, h: 100, top: '72%', left: '20%', rot: 10, color: 'var(--color-geo-4)', r: 16 },
    { w: 120, h: 120, top: '32%', left: '12%', rot: 18, color: 'var(--color-geo-5)', r: 14 },
    { w: 340, h: 110, top: '12%', right: '5%', rot: -5, color: 'var(--color-geo-6)', r: 26 },
    { w: 180, h: 200, top: '48%', right: '3%', rot: 8, color: 'var(--color-geo-7)', r: 18 },
    { w: 140, h: 90, bottom: '5%', right: '18%', rot: -6, color: 'var(--color-geo-8)', r: 14 },
    { w: 100, h: 160, top: '38%', left: '42%', rot: 14, color: 'var(--color-geo-9)', r: 12 },
    { w: 260, h: 80, bottom: '18%', left: '35%', rot: -2, color: 'var(--color-geo-10)', r: 16 },
    { w: 60, h: 60, top: '20%', left: '55%', rot: 30, color: 'var(--color-geo-11)', r: 10 },
    { w: 80, h: 50, bottom: '30%', left: '10%', rot: -15, color: 'var(--color-geo-12)', r: 10 },
    { w: 50, h: 70, top: '65%', right: '30%', rot: 22, color: 'var(--color-geo-13)', r: 8 },
  ];

  return (
    <>
      {blocks.map((b, i) => (
        <div key={i} className="absolute pointer-events-none" style={{
          width: b.w, height: b.h,
          top: b.top, left: b.left, right: b.right, bottom: b.bottom,
          transform: `rotate(${b.rot}deg)`,
          background: b.color,
          borderRadius: b.r,
          backdropFilter: 'blur(1px)',
          boxShadow: 'var(--color-geo-shadow)',
        }} />
      ))}
    </>
  );
}

/* ─────────────────────────────────────────────
   2.5D 等距 Q 版机器人
───────────────────────────────────────────── */
function Robot3D() {
  return (
    <div className="relative" style={{ width: 150, height: 185, filter: 'drop-shadow(0 18px 32px rgba(22,119,255,0.22))' }}>
      {/* ── 头部 ── */}
      <div className="absolute" style={{
        width: 112, height: 96, borderRadius: '56px 56px 40px 40px',
        background: 'linear-gradient(155deg, #ffffff 0%, #f7faff 30%, #e4eef8 70%, #d0dff0 100%)',
        left: '50%', top: 6, transform: 'translateX(-50%)',
        boxShadow: '0 12px 36px rgba(22,119,255,0.16), inset 0 4px 8px rgba(255,255,255,0.95), inset 0 -6px 14px rgba(0,0,0,0.05)',
      }}>
        {/* 左上高光 */}
        <div className="absolute" style={{ width: 44, height: 20, borderRadius: '50%', background: 'rgba(255,255,255,0.8)', top: 4, left: 10, filter: 'blur(5px)' }} />
        {/* 右下暗部 */}
        <div className="absolute" style={{ width: 50, height: 16, borderRadius: '50%', background: 'rgba(0,0,0,0.04)', bottom: 6, right: 6, filter: 'blur(4px)' }} />

        {/* 深蓝色发光面罩 */}
        <div className="absolute" style={{
          width: 86, height: 48, borderRadius: 26,
          background: 'linear-gradient(180deg, #1a3a6b 0%, #0f2848 60%, #091e36 100%)',
          left: '50%', top: 26, transform: 'translateX(-50%)',
          boxShadow: 'inset 0 4px 12px rgba(0,0,0,0.55), 0 0 20px rgba(22,119,255,0.18)',
        }}>
          {/* 面罩内上沿高光 */}
          <div className="absolute" style={{ width: 60, height: 6, borderRadius: '50%', background: 'rgba(79,195,247,0.15)', top: 2, left: '50%', transform: 'translateX(-50%)', filter: 'blur(2px)' }} />

          {/* 左眼 */}
          <div className="absolute" style={{
            width: 20, height: 20, borderRadius: '50%',
            background: 'radial-gradient(circle at 38% 32%, #b8f0ff 0%, #4fc3f7 40%, #2196f3 80%, #1565c0 100%)',
            left: 14, top: 14,
            boxShadow: '0 0 16px rgba(79,195,247,1), 0 0 32px rgba(79,195,247,0.4)',
          }}>
            <div className="absolute" style={{ width: 7, height: 7, borderRadius: '50%', background: '#fff', top: 3, left: 4 }} />
            <div className="absolute" style={{ width: 3, height: 3, borderRadius: '50%', background: 'rgba(255,255,255,0.6)', bottom: 4, right: 3 }} />
          </div>
          {/* 右眼 */}
          <div className="absolute" style={{
            width: 20, height: 20, borderRadius: '50%',
            background: 'radial-gradient(circle at 38% 32%, #b8f0ff 0%, #4fc3f7 40%, #2196f3 80%, #1565c0 100%)',
            right: 14, top: 14,
            boxShadow: '0 0 16px rgba(79,195,247,1), 0 0 32px rgba(79,195,247,0.4)',
          }}>
            <div className="absolute" style={{ width: 7, height: 7, borderRadius: '50%', background: '#fff', top: 3, left: 4 }} />
            <div className="absolute" style={{ width: 3, height: 3, borderRadius: '50%', background: 'rgba(255,255,255,0.6)', bottom: 4, right: 3 }} />
          </div>
        </div>
      </div>

      {/* ── 左耳机 ── */}
      <div className="absolute" style={{
        width: 22, height: 34, borderRadius: 11,
        background: 'linear-gradient(145deg, #6db3f8 0%, #1677ff 45%, #0d5bd6 100%)',
        left: -4, top: 32,
        boxShadow: '0 4px 12px rgba(22,119,255,0.45), inset 0 2px 4px rgba(255,255,255,0.3), inset 0 -2px 4px rgba(0,0,0,0.15)',
      }}>
        <div className="absolute" style={{ width: 8, height: 14, borderRadius: '50%', background: 'rgba(255,255,255,0.15)', top: 4, left: 3 }} />
      </div>
      {/* ── 右耳机 ── */}
      <div className="absolute" style={{
        width: 22, height: 34, borderRadius: 11,
        background: 'linear-gradient(145deg, #6db3f8 0%, #1677ff 45%, #0d5bd6 100%)',
        right: -4, top: 32,
        boxShadow: '0 4px 12px rgba(22,119,255,0.45), inset 0 2px 4px rgba(255,255,255,0.3), inset 0 -2px 4px rgba(0,0,0,0.15)',
      }}>
        <div className="absolute" style={{ width: 8, height: 14, borderRadius: '50%', background: 'rgba(255,255,255,0.15)', top: 4, left: 3 }} />
      </div>

      {/* ── 头顶指示灯 ── */}
      <div className="absolute" style={{ left: '50%', top: -14, transform: 'translateX(-50%)' }}>
        <div style={{ width: 3, height: 14, background: 'linear-gradient(180deg, #c8e0f8, #90bce0)', margin: '0 auto', borderRadius: 1.5 }} />
        <div style={{
          width: 30, height: 9, borderRadius: 5,
          background: 'linear-gradient(90deg, #7ec4ff 0%, #1677ff 40%, #7ec4ff 100%)',
          boxShadow: '0 0 14px rgba(22,119,255,0.75), 0 0 5px rgba(22,119,255,0.45)',
          marginTop: -1, marginLeft: -13.5,
        }} />
      </div>

      {/* ── 身体 ── */}
      <div className="absolute" style={{
        width: 88, height: 62, borderRadius: '30px 30px 24px 24px',
        background: 'linear-gradient(155deg, #ffffff 0%, #f2f7ff 35%, #dee8f5 75%, #cddcee 100%)',
        left: '50%', top: 102, transform: 'translateX(-50%)',
        boxShadow: '0 12px 28px rgba(22,119,255,0.14), inset 0 4px 8px rgba(255,255,255,0.85), inset 0 -5px 10px rgba(0,0,0,0.05)',
      }}>
        {/* 身体左上高光 */}
        <div className="absolute" style={{ width: 30, height: 14, borderRadius: '50%', background: 'rgba(255,255,255,0.7)', top: 4, left: 14, filter: 'blur(3px)' }} />
        {/* 身体右下暗部 */}
        <div className="absolute" style={{ width: 36, height: 10, borderRadius: '50%', background: 'rgba(0,0,0,0.03)', bottom: 4, right: 8, filter: 'blur(3px)' }} />
        {/* 胸部蓝色指示灯 */}
        <div className="absolute" style={{
          width: 24, height: 24, borderRadius: '50%',
          background: 'radial-gradient(circle at 36% 36%, #b0ecff 0%, #4fc3f7 35%, #1677ff 85%, #0d47a1 100%)',
          left: '50%', top: 14, transform: 'translateX(-50%)',
          boxShadow: '0 0 18px rgba(22,119,255,0.6), 0 0 6px rgba(79,195,247,0.4)',
        }}>
          <div className="absolute" style={{ width: 8, height: 8, borderRadius: '50%', background: 'rgba(255,255,255,0.5)', top: 3, left: 4 }} />
        </div>
        {/* 装饰线 */}
        <div className="absolute" style={{ width: 46, height: 2, borderRadius: 1, background: 'linear-gradient(90deg, transparent, #c0d8f0, transparent)', left: '50%', bottom: 10, transform: 'translateX(-50%)' }} />
      </div>

      {/* ── 左手 ── */}
      <div className="absolute" style={{
        width: 22, height: 22, borderRadius: '50%',
        background: 'linear-gradient(145deg, #ffffff 0%, #dce8f5 60%, #c0d4e8 100%)',
        left: 2, top: 120,
        boxShadow: '0 4px 12px rgba(22,119,255,0.14), inset 0 2px 4px rgba(255,255,255,0.8), inset 0 -2px 4px rgba(0,0,0,0.05)',
      }} />
      {/* ── 右手 ── */}
      <div className="absolute" style={{
        width: 22, height: 22, borderRadius: '50%',
        background: 'linear-gradient(145deg, #ffffff 0%, #dce8f5 60%, #c0d4e8 100%)',
        right: 2, top: 120,
        boxShadow: '0 4px 12px rgba(22,119,255,0.14), inset 0 2px 4px rgba(255,255,255,0.8), inset 0 -2px 4px rgba(0,0,0,0.05)',
      }} />

      {/* ── 底部悬浮投影 ── */}
      <div className="absolute" style={{
        width: 70, height: 12, borderRadius: '50%',
        background: 'radial-gradient(ellipse, rgba(22,119,255,0.18) 0%, transparent 70%)',
        left: '50%', bottom: -8, transform: 'translateX(-50%)',
        filter: 'blur(3px)',
      }} />
    </div>
  );
}

/* ─────────────────────────────────────────────
   2.5D 等距立体同心圆平台
───────────────────────────────────────────── */
function Platform3D() {
  return (
    <div className="relative" style={{ width: 270, height: 90 }}>
      {/* 第三层（最底、最大） */}
      <div className="absolute" style={{ left: '50%', top: 44, transform: 'translateX(-50%)' }}>
        <div style={{ width: 270, height: 22, borderRadius: '0 0 135px 135px', background: 'linear-gradient(180deg, #8baed0 0%, #7199be 100%)' }} />
        <div style={{ width: 270, height: 56, borderRadius: '50%', background: 'linear-gradient(180deg, #d0e4fa 0%, #b8d4f4 100%)', marginTop: -10, boxShadow: '0 8px 24px rgba(22,119,255,0.1)' }} />
      </div>
      {/* 第二层 */}
      <div className="absolute" style={{ left: '50%', top: 24, transform: 'translateX(-50%)' }}>
        <div style={{ width: 208, height: 18, borderRadius: '0 0 104px 104px', background: 'linear-gradient(180deg, #6e9acc 0%, #5a88bc 100%)' }} />
        <div style={{ width: 208, height: 46, borderRadius: '50%', background: 'linear-gradient(180deg, #b0ccf2 0%, #9abce6 100%)', marginTop: -9, boxShadow: '0 6px 16px rgba(22,119,255,0.14)' }} />
      </div>
      {/* 第一层（最上、最小） */}
      <div className="absolute" style={{ left: '50%', top: 0, transform: 'translateX(-50%)' }}>
        <div style={{ width: 156, height: 16, borderRadius: '0 0 78px 78px', background: 'linear-gradient(180deg, #3d7ec8 0%, #1677ff 100%)' }} />
        <div style={{
          width: 156, height: 38, borderRadius: '50%',
          background: 'linear-gradient(135deg, #a0ccfd 0%, #6aa6e8 35%, #1677ff 100%)',
          marginTop: -8,
          boxShadow: '0 8px 32px rgba(22,119,255,0.38), inset 0 -3px 10px rgba(0,0,0,0.12)',
          position: 'relative',
        }}>
          <div className="absolute" style={{ width: 96, height: 20, borderRadius: '50%', border: '1.5px solid rgba(255,255,255,0.3)', left: '50%', top: '50%', transform: 'translate(-50%,-50%)' }} />
          <div className="absolute" style={{ width: 60, height: 14, borderRadius: '50%', border: '1px solid rgba(255,255,255,0.22)', left: '50%', top: '50%', transform: 'translate(-50%,-50%)' }} />
          <div className="absolute" style={{ width: 30, height: 8, borderRadius: '50%', border: '1px solid rgba(255,255,255,0.15)', left: '50%', top: '50%', transform: 'translate(-50%,-50%)' }} />
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   2.5D 等距环绕图标节点（立体圆台底座）
───────────────────────────────────────────── */
function IconNode3D({ icon, style, delay = 0 }: { icon: React.ReactNode; style: React.CSSProperties; delay?: number }) {
  return (
    <div className="absolute icon-fade" style={{ zIndex: 8, animation: `iconFadeIn 0.5s ease-out ${delay}s both`, ...style }}>
      {/* 圆台侧面（厚度） */}
      <div style={{
        width: 58, height: 18, borderRadius: '0 0 29px 29px',
        background: 'linear-gradient(180deg, #8aafc8 0%, #6e98b4 50%, #5c88a6 100%)',
        marginTop: 48,
        boxShadow: '0 4px 8px rgba(0,0,0,0.08)',
      }} />
      {/* 圆台顶面 */}
      <div style={{
        width: 58, height: 58, borderRadius: '50%',
        background: 'linear-gradient(145deg, #ffffff 0%, #eef4ff 60%, #dce8f8 100%)',
        boxShadow: '0 6px 20px rgba(22,119,255,0.16), 0 2px 6px rgba(0,0,0,0.06)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        marginTop: -53,
      }}>
        {/* 内圈凹陷 */}
        <div style={{
          width: 44, height: 44, borderRadius: '50%',
          background: 'linear-gradient(145deg, #ffffff 0%, #f4f8ff 100%)',
          boxShadow: 'inset 0 2px 6px rgba(22,119,255,0.1), inset 0 -1px 3px rgba(255,255,255,0.9), 0 1px 3px rgba(255,255,255,0.8)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#1677ff',
        }}>
          {icon}
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   插画场景（机器人 + 平台 + 图标 + 连接线）
───────────────────────────────────────────── */
export function IllustrationScene() {
  const iconPositions = [
    { x: 60, y: 100 },
    { x: 320, y: 100 },
    { x: 25, y: 230 },
    { x: 355, y: 230 },
    { x: 60, y: 355 },
    { x: 320, y: 355 },
  ];
  const centerX = 190;
  const centerY = 220;

  return (
    <div className="relative" style={{ width: 400, height: 440 }}>
      {/* 微动效关键帧 */}
      <style>{`
        @keyframes robotFloat {
          0%, 100% { transform: translateX(-50%) translateY(0); }
          50% { transform: translateX(-50%) translateY(-6px); }
        }
        @keyframes iconFadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @media (prefers-reduced-motion: reduce) {
          .robot-float { animation: none !important; }
          .icon-fade { animation: none !important; }
        }
      `}</style>
      {/* SVG 发光连接线 */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 1 }}>
        <defs>
          <linearGradient id="lineGlow" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#1677ff" stopOpacity="0.15" />
            <stop offset="50%" stopColor="#1677ff" stopOpacity="0.4" />
            <stop offset="100%" stopColor="#1677ff" stopOpacity="0.15" />
          </linearGradient>
        </defs>
        {iconPositions.map((pos, i) => (
          <line key={i} x1={centerX} y1={centerY} x2={pos.x + 29} y2={pos.y + 29}
            stroke="url(#lineGlow)" strokeWidth="2" strokeDasharray="8 5" />
        ))}
        {iconPositions.map((pos, i) => {
          const next = iconPositions[(i + 1) % iconPositions.length];
          return (
            <line key={`ring-${i}`}
              x1={pos.x + 29} y1={pos.y + 29}
              x2={next.x + 29} y2={next.y + 29}
              stroke="url(#lineGlow)" strokeWidth="1.5" opacity="0.6" />
          );
        })}
      </svg>

      {/* 机器人 */}
      <div className="absolute robot-float" style={{ left: '50%', top: 100, transform: 'translateX(-50%)', zIndex: 10, animation: 'robotFloat 3.5s ease-in-out infinite, iconFadeIn 0.6s ease-out' }}>
        <Robot3D />
      </div>

      {/* 平台 */}
      <div className="absolute" style={{ left: '50%', top: 260, transform: 'translateX(-50%)', zIndex: 5 }}>
        <Platform3D />
      </div>

      {/* 6 个环绕图标 */}
      <IconNode3D icon={<Folder size={20} />} delay={0.1} style={{ left: iconPositions[0].x, top: iconPositions[0].y }} />
      <IconNode3D icon={<Shield size={20} />} delay={0.2} style={{ left: iconPositions[1].x, top: iconPositions[1].y }} />
      <IconNode3D icon={<Camera size={20} />} delay={0.3} style={{ left: iconPositions[2].x, top: iconPositions[2].y }} />
      <IconNode3D icon={<Cloud size={20} />} delay={0.4} style={{ left: iconPositions[3].x, top: iconPositions[3].y }} />
      <IconNode3D icon={<Monitor size={20} />} delay={0.5} style={{ left: iconPositions[4].x, top: iconPositions[4].y }} />
      <IconNode3D icon={<Globe size={20} />} delay={0.6} style={{ left: iconPositions[5].x, top: iconPositions[5].y }} />
    </div>
  );
}
